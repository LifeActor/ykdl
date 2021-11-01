import gzip
import zlib
import socket
import functools
from io import BytesIO
from logging import getLogger
from collections import defaultdict
from http.client import HTTPResponse as _HTTPResponse
from urllib.parse import urlencode
from urllib.request import Request, install_opener, build_opener, \
                           HTTPRedirectHandler as _HTTPRedirectHandler, \
                           AbstractHTTPHandler, URLError, HTTPError
try:
    from queue import SimpleQueue as Queue, Empty  # py37 and above
except ImportError:
    from queue import Queue, Empty

from .match import match1


logger = getLogger('html')


# Add persistent connections feature into urllib.request

_http_conn_cache = defaultdict(Queue)
_headers_template = {k: '' for k in ('Host', 'User-Agent', 'Accept')}

def _do_open(self, http_class, req, **http_conn_args):
    '''Return an HTTPResponse object for the request, using http_class.

    http_class must implement the HTTPConnection API from http.client.
    
    There has some codes to handle persistent connections
    '''
    host = req.host
    if not host:
        raise URLError('no host given')

    timeout = req.timeout
    conn_key = req._full_url[:req._full_url.find('/', 9)]
    queue = _http_conn_cache[conn_key]

    try:
        h = queue.get_nowait()
    except Empty:
        h = http_class(host, timeout=timeout, **http_conn_args)
    else:
        h.sock.setblocking(False)
        try:
            h.sock.recv(1)
            h.close()  # drop legacy and disconnection
        except:
            if timeout is socket._GLOBAL_DEFAULT_TIMEOUT:
                timeout = socket.getdefaulttimeout()
            h.sock.settimeout(timeout)

    h.set_debuglevel(self._debuglevel)

    # keep the sequence in template
    headers = _headers_template.copy()
    headers.update(req.headers)
    headers.update(req.unredirected_hdrs)
    headers = {k.title(): v for k, v in headers.items()}

    for hdr in ('Connection', 'Proxy-Connection'):  # always do, ignore input
        headers.pop(hdr, None)

    # urllib.request only use header Proxy-Authorization
    # Move all tunnel headers which user input, that has be needed
    tunnel_headers = {k: v for k, v in headers.items() if k.startswith('Proxy-')}
    for hdr in tunnel_headers:
        headers.pop(hdr)
    if req._tunnel_host and h.sock is None:  # add reuse check to bypass
        h.set_tunnel(req._tunnel_host, headers=tunnel_headers)

    req_args = {}
    if hasattr(http_class, '_is_textIO'):  # py35 and below are False
                                           # uncommonly use in our modules
        req_args['encode_chunked'] = req.has_header('Transfer-encoding')
    try:
        try:
            h.request(req.get_method(), req.selector, req.data, headers,
                      **req_args)
        except OSError as err:  # timeout error
            raise URLError(err)
        r = h.getresponse()
    except:
        h.close()
        raise

    # Use functools.partial to avoid circular references
    r.queue_put = functools.partial(queue.put, h)

    r.url = req.get_full_url()
    r.msg = r.reason
    return r

def _close_conn(self):
    fp, self.fp = self.fp, None
    try:
        fp.close()
    finally:
        if hasattr(self, 'queue_put'):
            self.queue_put()    # last request is over, ready for reuse
            del self.queue_put  # clear, can be run only once

AbstractHTTPHandler.do_open = _do_open   #
_HTTPResponse._close_conn = _close_conn  # monkey patch, but secure


# Custom HTTP redirect handler

class HTTPRedirectHandler(_HTTPRedirectHandler):
    '''Log all responses during redirect, support specify max redirections
    
    MUST call from get_response(), or fallback to origin HTTPRedirectHandler
    '''
    max_repeats = 2
    max_redirections = 5
    rmethod = 'GET', 'HEAD', 'POST'  # allow redirect POST method
    amcodes = 301, 302, 303          # codes redirect alterable method
    fmcodes = 307, 308               # codes redirect fixedly method
    rcodes = amcodes + fmcodes

    def __init__(self):
        for code in self.rcodes:
            setattr(self, 'http_error_%d' % code, self.http_error_code)

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # If does not request from this module, go to origin method
        if not hasattr(req, 'locations'):
            if code == 308 and not hasattr(_HTTPRedirectHandler, 'http_error_308'):
                return
            return super().redirect_request(req, fp, code, msg, headers, newurl)

        logger.debug('Redirect to URL: ' + newurl)
        req.locations.append(newurl)

        method = req.get_method()
        if method not in self.rmethod:
            raise HTTPError(req.full_url, code, msg, headers, fp)

        data = req.data  # used by fixedly method redirection
        newheaders = {k.lower(): v for k, v in req.headers.items()}
        if code in self.rmethod:
            for header in ('content-length', 'content-type', 'transfer-encoding'):
                newheaders.pop(header, None)
            data = None
            if method != 'HEAD':
                method = 'GET'

        # Useless in our modules, memo for somebody may needs
        #newurl = newurl.replace(' ', '%20')

        req.newreq = newreq = Request(newurl, data=data, headers=newheaders,
                                      origin_req_host=req.origin_req_host,
                                      unverifiable=True, method=method)

        # Important attributes MUST be passed to new request
        newreq.headget = req.headget
        newreq.locations = req.locations
        newreq.responses = req.responses
        return newreq

    def http_error_code(self, req, fp, code, msg, headers):
        # If does not request from this module, go to origin method
        if not hasattr(req, 'locations'):
            if code == 308 and not hasattr(_HTTPRedirectHandler, 'http_error_308'):
                return
            return super().http_error_302(req, fp, code, msg, headers)

        if req.max_redirections is not None:
            self.max_redirections = req.max_redirections
        if not req.locations:
            # origin request / first response
            req.responses.append(HTTPResponse(req, fp))
        try:
            newres = super().http_error_302(req, fp, code, msg, headers)
        except HTTPError:
            if req.headget or fp._method == 'HEAD':
                fp.url = req.locations[-1]  # fake response, reuse last one
                return fp
            raise
        else:
            req.responses.append(HTTPResponse(req.newreq, newres))
        finally:
            try:
                del req.newreq  # clear circular reference
            except AttributeError:
                pass
        return newres


# Custom HTTP response

class HTTPResponse:
    def __init__(self, request, response, encoding=None, *, finish=False):
        '''Wrap urllib.request.Request and http.client.HTTPResponse.

        Params: `encoding` is used to decode responsed content.

                `finish`, only has effect on redirections.

                    `False` is used by sub-responses (default),
                    `True` is used by main response (explicit).

                `request` and `response` referred to see get_response() codes.
        '''
        self.request = request
        self.method = response._method
        self.url = response.url
        self.locations = request.locations
        self.status = response.status
        self.reason = response.reason
        self.headers = self.msg = headers = response.headers
        self._encoding = encoding
        if finish and self.locations:
            # Redirected response has been closed, copy from last one
            response = request.responses[-1]
            self.raw = response.raw
            self.content = response.content
            return
        self.raw = data = not request.headget and response.read() or b''
        response.close()
        if data:
            # Handle HTTP compression for gzip and deflate (zlib)
            ce = None
            if 'Content-Encoding' in headers:
                ce = headers['Content-Encoding']
            else:
                payload = headers.get_payload()
                if isinstance(payload, list):
                    payload = payload[0]
                if isinstance(payload, str):
                    ce =  match1(payload, '(?i)content-encoding:\s*([\w-]+)')
            if ce == 'gzip':
                data = ungzip(data)
            elif ce == 'deflate':
                data = undeflate(data)
        self.content = data

    def __repr__(self):
        return '<%s object at %s>' % (type(self).__name__, hex(id(self)))

    def __str__(self):
        return self.text

    def close(self):
        '''HTTP response always has been closed in init, do nothing here.'''
        pass

    @property
    def encoding(self):
        return self._encoding

    @encoding.getter
    def encoding(self, encoding):
        '''Set encoding will reset attribute `text`'''
        self._encoding = encoding
        try:
            del self._text
        except AttributeError:
            pass

    @property
    def text(self):
        '''Return the decoded text, encoding can be specify or auto-detect.'''
        try:
            return self._text
        except AttributeError:
            pass
        def decode(encoding):
            if isinstance(encoding, bytes):
                encoding = encoding.decode()
            if isinstance(encoding, str):
                try:
                    self._text = self.content.decode(encoding, errors='replace')
                except:
                    logger.debug('Try decode with encoding %r fail', encoding)
                else:
                    return True
        decode(self._encoding) or \
        decode(self.headers.get_content_charset()) or \
        'json' in self.headers.get_content_subtype().lower() and \
        decode('utf-8') or \
        decode(match1(self.content[:1024],
                      b'(?i)<meta[^>]+charset=["\']?([\w-]+)',
                      b'(?i)<\\?xml[^>]+encoding=["\']?([\w-]+)')) or \
        decode('utf-8')  # fallback
        assert hasattr(self, '_text'), 'Decode fail, URL: ' + self.url
        return self._text

    def json(self):
        '''Return a object which deserialize from JSON text.'''
        return json.loads(self.text)

    def xml(self):
        '''Return a DOM (simple implementation) which parse from XML text.'''
        from xml.dom.minidom import parseString
        return parseString(self.text)

for _ in ('getheader', 'getheaders', 'info', 'geturl', 'getcode'):
    setattr(HTTPResponse, _, getattr(_HTTPResponse, _))


# utils

_opener = None
_default_handlers = []

def add_default_handler(handler):
    if isinstance(handler, type):
        handler = handler()
    if isinstance(handler, _HTTPRedirectHandler):
        logger.warning('HTTPRedirectHandler is not custom!')
        return
    remove = []
    for default_handler in _default_handlers:
        if isinstance(handler, type(default_handler)) or \
                isinstance(default_handler, type(handler)):
            remove.append(default_handler)
    for _handler in remove:
        _default_handlers.remove(_handler)
        logger.debug('Remove %s from default handlers', _handler)
    _default_handlers.append(handler)
    logger.debug('Add %s to default handlers', handler)

def install_default_handlers():
    # Always use our custom HTTPRedirectHandler
    global _opener
    _opener = build_opener(HTTPRedirectHandler, *_default_handlers)
    install_opener(_opener)

_default_fake_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:60.1) Gecko/20100101 Firefox/60.1'
}
fake_headers = _default_fake_headers.copy()

def reset_headers():
    '''Reset the fake_headers to default keys and values'''
    fake_headers.clear()
    fake_headers.update(_default_fake_headers)

def add_header(key, value):
    '''Set the fake_headers[key] to value'''
    global fake_headers
    fake_headers[key] = value

def ungzip(data):
    '''Decompresses data for Content-Encoding: gzip.'''
    return gzip.GzipFile(fileobj=BytesIO(data)).read()

def undeflate(data):
    '''Decompresses data for Content-Encoding: deflate.'''
    decompressobj = zlib.decompressobj(-zlib.MAX_WBITS)
    return decompressobj.decompress(data) + decompressobj.flush()

def get_response(url, headers=fake_headers, data=None, method='GET',
                      max_redirections=None, encoding=None):
    '''Fetch the response of giving URL.

    Return: response, If redirections > max_redirections > 0,
            this is fake except its attribute `url`.
    '''
    global _opener
    headget = method == 'HEADGET'  # if True the response will be closed
    if headget:                    # without read content
        method = 'GET'
    elif method != 'HEAD':
        logger.debug('get_response> URL: ' + url)
    if data:
        if isinstance(data, str):
            data = data.encode()
        elif not hasattr(data, 'read'):
            try:
                memoryview(data)
            except TypeError:
                try:
                    data = urlencode(data).encode()
                except TypeError:
                    pass
    req = Request(url, headers=headers, data=data, method=method)
    req.headget = headget
    req.max_redirections = max_redirections
    req.redirect_dict = {}  # init here allow disable redirect
    req.locations = []
    req.responses = responses = []
    #if cookies_txt:
    #    cookies_txt.add_cookie_header(req)
    #    req.headers.update(req.unredirected_hdrs)
    if encoding == 'ignore':
        encoding = None
    if _opener is None:
        install_default_handlers()
    try:
        response = HTTPResponse(req, _opener.open(req), encoding, finish=True)
    finally:
        for r in responses:
            del r.request.responses  # clear circular reference
    response.responses = responses
    return response

def get_head_response(url, headers=fake_headers, max_redirections=0):
    '''Fetch the response of giving URL in HEAD mode.

    Return: response, If redirections > max_redirections > 0,
            this is fake except its attribute `url`.
    '''
    logger.debug('get_head_response> URL: ' + url)
    try:
        response = get_response(url, headers=headers, method='HEAD',
                                max_redirections=max_redirections)
    except IOError as e:
        # Maybe HEAD method is not supported, retry
        if match1(str(e), 'HTTP Error (40[345])'):
            logger.debug('get_head_response> HEAD failed, try GET')
            response = get_response(url, headers=headers, method='HEADGET',
                                    max_redirections=max_redirections)
        else:
            raise
    return response

def get_location(*args, **kwargs):
    '''Try fetch the redirected location of giving URL.

    Params: same as get_head_response().

    Return: URL.
    '''
    response = get_head_response(*args, **kwargs)
    return response.url

def get_location_and_header(*args, **kwargs):
    '''Try fetch the redirected location and the headers of giving URL.

    Params: same as get_head_response().
            If redirections > max_redirections > 0, returned headers is fake.

    Return: URL and headers.
    '''
    response = get_head_response(*args, **kwargs)
    return response.url, response.headers

def get_content_and_location(*args, **kwargs):
    '''Try fetch the content and the redirected location of giving URL.

    Params: same as get_response().

    Return: content (encoding=='ignore') or decoded content, and URL.
    '''
    response = get_response(*args, **kwargs)
    if kwargs.get('encoding') == 'ignore':
        return response.content, response.url
    return response.text, response.url

def get_content(*args, **kwargs):
    '''Fetch the content of giving URL.

    Params: same as get_response().

    Return: content (encoding=='ignore') or decoded content.
    '''
    return get_content_and_location(*args, **kwargs)[0]

def url_info(url, headers=None, size=False):
    # TODO: modify to return named(filename, ext, size, ...)
    # in case url is http(s)://host/a/b/c.dd?ee&fff&gg
    # below is to get c.dd
    f = url.split('?')[0].split('/')[-1]
    # check . in c.dd, get dd if true
    if '.' in f:
        ext = f.split('.')[-1]
    else:
        ext = ''
    return '', ext, 0
