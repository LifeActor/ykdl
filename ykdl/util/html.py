import re
from logging import getLogger
from collections import defaultdict
from urllib.parse import urlencode
from urllib.request import Request, urlopen, install_opener, build_opener, \
                           AbstractHTTPHandler, URLError
try:
    from queue import SimpleQueue as Queue, Empty  # py37 and above
except ImportError:
    from queue import Queue, Empty

from .match import match1


logger = getLogger("html")

_http_conn_cache = defaultdict(Queue)
_headers_template = {k: '' for k in ('Host', 'User-Agent', 'Accept')}

def _do_open(self, http_class, req, **http_conn_args):
    """Return an HTTPResponse object for the request, using http_class.

    http_class must implement the HTTPConnection API from http.client.
    
    there has codes to handle persistent connections
    """
    host = req.host
    if not host:
        raise URLError('no host given')

    conn_key = req._full_url[:req._full_url.find('/', 9)]
    queue = _http_conn_cache[conn_key]

    try:
        h = queue.get_nowait()
    except Empty:
        h = http_class(host, timeout=req.timeout, **http_conn_args)
    h.set_debuglevel(self._debuglevel)

    # keep the sequence in template
    headers = _headers_template.copy()
    headers.update(req.headers)
    headers.update(req.unredirected_hdrs)
    headers = {k.title(): v for k, v in headers.items()}

    for hdr in ('Connection', 'Proxy-Connection'):  # always do, ignore input
        headers.pop(hdr, None)

    # urllib.request only use header Proxy-Authorization
    # move all tunnel headers which user input, that has be needed
    tunnel_headers = {k: v for k, v in headers.items() if k.startswith('Proxy-')}
    for hdr in tunnel_headers:
        headers.pop(hdr)
    if req._tunnel_host:
        if h.sock is None:  # add reuse check to bypass
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
        queue.put(h)  # errors happen on socket
        raise         # but connect instances are still OK of reuse

    def _close_conn():
        fp, r.fp = r.fp, None
        fp.close()
        queue.put(h)  # last request is over, ready for reuse

    r._close_conn = _close_conn

    r.url = req.get_full_url()
    r.msg = r.reason
    return r

AbstractHTTPHandler.do_open = _do_open  # monkey patch

default_handlers = []

def add_default_handler(handler):
    if isinstance(handler, type):
        handler = handler()
    remove = []
    for default_handler in default_handlers:
        if isinstance(handler, type(default_handler)) or \
                isinstance(default_handler, type(handler)):
            remove.append(default_handler)
    for _handler in remove:
        default_handlers.remove(_handler)
        logger.debug('Remove %s from default handlers' % _handler)
    default_handlers.append(handler)
    logger.debug('Add %s to default handlers' % handler)

def install_default_handlers():
    install_opener(build_opener(*default_handlers))

fake_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:60.1) Gecko/20100101 Firefox/60.1'
}

def add_header(key, value):
    global fake_headers
    fake_headers[key] = value

def unicodize(text):
    return re.sub(r'\\u([0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f])', lambda x: chr(int(x.group(0)[2:], 16)), text)

def ungzip(data):
    """Decompresses data for Content-Encoding: gzip.
    """
    from io import BytesIO
    import gzip
    buffer = BytesIO(data)
    f = gzip.GzipFile(fileobj=buffer)
    return f.read()

def undeflate(data):
    """Decompresses data for Content-Encoding: deflate.
    (the zlib compression is used.)
    """
    import zlib
    decompressobj = zlib.decompressobj(-zlib.MAX_WBITS)
    return decompressobj.decompress(data)+decompressobj.flush()

def get_response(url, headers=fake_headers, data=None):
    req = Request(url, headers=headers, data=data)
    #if cookies_txt:
    #    cookies_txt.add_cookie_header(req)
    #    req.headers.update(req.unredirected_hdrs)
    return urlopen(req)

def get_head_response(url, headers=fake_headers):
    logger.debug('get_head_response> URL: ' + url)
    try:
        req = Request(url, headers=headers, method='HEAD')
        response = urlopen(req)
    except IOError as e:
        # if HEAD method is not supported
        if match1(str(e), 'HTTP Error (40[345])'):
            logger.debug('get_head_response> HEAD failed, try GET')
            response = get_response(url, headers=headers)
        else:
            raise
    response.close()
    # urllib will follow redirections and it's too much code to tell urllib
    # not to do that
    return response

def get_location(url, headers=fake_headers):
    response = get_head_response(url, headers=headers)
    return response.geturl()

def get_location_and_header(url, headers=fake_headers):
    response = get_head_response(url, headers=headers)
    return response.geturl(), response.info()

def get_content_and_location(url, headers=fake_headers, data=None, charset=None):
    """Gets the content of a URL via sending a HTTP GET request.

    Args:
        url: A URL.
        headers: Request headers used by the client.

    Returns:
        The content as a string.
    """
    logger.debug('get_content> URL: ' + url)
    response = get_response(url, headers=headers, data=data)
    data = response.read()
    rurl = response.geturl()
    if rurl != url:
        logger.debug('get_content> redirect to URL: ' + rurl)

    # Handle HTTP compression for gzip and deflate (zlib)
    resheader = response.info()
    if 'Content-Encoding' in resheader:
        content_encoding = resheader['Content-Encoding']
    elif hasattr(resheader, 'get_payload'):
        payload = resheader.get_payload()
        if isinstance(payload, str):
            content_encoding =  match1(payload, 'Content-Encoding:\s*([\w-]+)')
        else:
            content_encoding = None
    else:
        content_encoding = None
    if content_encoding == 'gzip':
        data = ungzip(data)
    elif content_encoding == 'deflate':
        data = undeflate(data)

    if charset == 'ignore':
        return data, rurl

    # Decode the response body
    charset = charset or resheader.get_content_charset() or \
                match1(str(data), 'charset="?([\w-]+)') or 'utf-8'
    logger.debug('get_content> Charset: ' + charset)
    try:
        data = data.decode(charset, errors='replace')
    except:
        logger.warning('wrong charset for {}'.format(url))
    return data, rurl

def get_content(url, headers=fake_headers, data=None, charset=None):
    return get_content_and_location(url, headers=headers, data=data, charset=charset)[0]

#DEPRECATED below, return None or 0
def url_size(url, faker=False):
    return 0

def urls_size(urls):
    return sum(map(url_size, urls))

def url_info(url, faker=False):
    # in case url is http(s)://host/a/b/c.dd?ee&fff&gg
    # below is to get c.dd
    f = url.split('?')[0].split('/')[-1]
    # check . in c.dd, get dd if true
    if '.' in f:
        ext = f.split('.')[-1]
    else:
        ext = ''
    return '', ext, 0
