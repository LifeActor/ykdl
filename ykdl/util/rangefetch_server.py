#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Multithreading range fetch via proxy server,
# use urllib3 to reusing connections.

from logging import getLogger
from ykdl.compact import (
    Queue, thread, urlsplit, SplitResult,
    HTTPStatus, BaseHTTPRequestHandler, SocketServer
    )

import urllib3
import re
import socket
from time import sleep

logger = getLogger('RangeFetch')

class LocalTCPServer(SocketServer.ThreadingTCPServer):

    request_queue_size = 2
    allow_reuse_address = True

    def server_bind(self):
        sock = self.socket
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, True)
        self.RequestHandlerClass.bufsize = sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
        SocketServer.TCPServer.server_bind(self)

    def server_close(self):
        self.shutdown()
        self.socket.close()

class RangeFetchHandler(BaseHTTPRequestHandler):
    '''
    HTTP Handler.

    :property scheme:
        Set the value to 'https' can connect remote server ues https.
    '''

    protocol_version = 'HTTP/1.1'
    scheme = 'http'

    def do_CONNECT(self):
        self.send_error(HTTPStatus.NOT_IMPLEMENTED,
            'Range fetch via HTTPS can not be supported!')

    def do_GET(self):
        url_parts = urlsplit(self.path)
        self.host = netloc = self.headers.get('Host') or url_parts.netloc
        self.url = SplitResult(self.scheme, netloc, url_parts.path, url_parts.query, '').geturl()
        
        need_rangefetch = not ('range=' in url_parts.query or
                               'live=1' in url_parts.query or
                               'range/' in url_parts.path
                               )
        range_start = range_end = 0

        if need_rangefetch:
            need_rangefetch = 1
            request_range = self.headers.get('Range')
            if request_range is not None:
                request_range = getbytes(request_range)
                if request_range:
                    range_start, range_end, range_other = request_range.group(1, 2, 3)
                    if not range_start or range_other:
                        # Unable to process unspecified start range or discontinuous range
                        range_start = 0
                        need_rangefetch = 0
                    else:
                        range_start = int(range_start)
                        if range_end:
                            range_end = int(range_end)
        else:
            need_rangefetch = -1

        if need_rangefetch is 1:
            RangeFetch(self, range_start, range_end).fetch()
        else:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR,
                'Range fetch can not be finished, url: %s' %  self.url)

class RangeFetch():

    expect_begin = 0
    _stopped = False
    proxy = None

    first_size = 1024 * 32
    max_size = 1024 * 32
    threads = 8
    delay = 0.5

    def __init__(self, handler, range_start, range_end):
        self.handler = handler
        self.bufsize = handler.bufsize
        self.write = handler.wfile.write
        self.url = handler.url
        self.headers = dict((k.title(), v) for k, v in handler.headers.items()
                           if not k.title().startswith('Proxy-'))
        # Set 'keep-alive'
        self.headers['Connection'] = 'keep-alive'

        self.range_start = range_start
        self.range_end = range_end

        self.delay_star_size = self.max_size * self.threads
        self.delay_cache_size = self.delay_star_size * 2

        if self.proxy:
            self.http = urllib3.ProxyManager(self.proxy, maxsize=self.threads + 2)
        else:
            self.http = urllib3.PoolManager(maxsize=self.threads + 2)
        self.firstrange = range_start, range_start + self.first_size - 1
        self.response = self.rangefetch(*self.firstrange)

        self.data_queue = Queue.PriorityQueue()
        self.range_queue = Queue.PriorityQueue()

    def rangefetch(self, range_start, range_end, max_tries=3):
        tries= 0
        headers = self.headers.copy()
        headers['Range'] = 'bytes=%d-%d' % (range_start, range_end)

        while True:
            response = self.http.request('GET', self.url, headers=headers, redirect=False, preload_content=False)

            redirect_location = response.get_redirect_location()
            if redirect_location:
                if not redirect_location.startswith(('http://', 'https://', '/')) :
                    redirect_location = '/' + redirect_location
                if redirect_location[0] == '/':
                    redirect_location = '%s://%s%s' % (self.handler.scheme, self.handler.host, redirect_location)
                self.url = redirect_location
                response.read()
                response.release_conn()
                continue

            if response.status == 206:
                return response

            tries += 1
            if tries >= max_tries:
                break
            sleep(2)

    def fetch(self):
        response_status = self.response.status
        response_headers = self.response.headers

        start, end, length = tuple(int(x) for x in getrange(response_headers['Content-Range']).group(1, 2, 3))
        content_length = end + 1 - start
        _end = length - 1
        if start == 0 and self.range_end in (0, _end) and 'Range' not in self.headers:
            response_status = 200
            response_headers['Content-Length'] = str(length)
            range_end = _end
            del response_headers['Content-Range']
        else:
            range_end = self.range_end or _end
            response_headers['Content-Range'] = 'bytes %s-%s/%s' % (start, range_end, length)
            length = range_end + 1
            response_headers['Content-Length'] = str(length - start)

        self.handler.send_response_only(response_status)
        for kv in response_headers.items():
            self.handler._headers_buffer.append(('%s: %s\r\n' % kv).encode())
        self.handler.end_headers()

        data_queue = self.data_queue
        range_queue = self.range_queue

        a = end + 1
        b = end
        n = (length - a) // self.max_size
        for _ in range(n):
            b += self.max_size
            range_queue.put((a, b))
            a = b + 1
        if length > a:
            range_queue.put((a, length - 1))

        for i in range(self.threads):
            spawn_later(self.delay * i, self.__fetchlet)

        has_peek = hasattr(data_queue, 'peek')
        peek_timeout = 30
        self.expect_begin = start

        while self.expect_begin < length:
            try:
                if has_peek:
                    begin, data = data_queue.peek(timeout=peek_timeout)
                    if self.expect_begin == begin:
                        data_queue.get()
                    elif self.expect_begin < begin:
                        sleep(0.1)
                        continue
                    else:
                        logger.error('error: begin(%r) < expect_begin(%r), exit.'% (begin, self.expect_begin))
                        break
                else:
                    begin, data = data_queue.get(timeout=peek_timeout)
                    if self.expect_begin == begin:
                        pass
                    elif self.expect_begin < begin:
                        data_queue.put((begin, data))
                        sleep(0.1)
                        continue
                    else:
                        logger.error('error: begin(%r) < expect_begin(%r), exit.'% (begin, self.expect_begin))
                        break
            except Queue.Empty:
                logger.error('data_queue peek timedout break')
                break
            try:
                self.write(data)
                self.expect_begin += len(data)
            except Exception as e:
                logger.warning('disconnected: %r, %r' % (self.url, e))
                break
        self._stopped = True

    def __fetchlet(self):
        data_queue = self.data_queue
        range_queue = self.range_queue

        while True:
            if self._stopped:
                return

            if self.response:
                response, self.response = self.response, None
                start, end = self.firstrange
            else:
                try:
                    start, end = range_queue.get(timeout=1)
                except Queue.Empty:
                    return
                while ((start - self.expect_begin) > self.delay_star_size and
                        data_queue.qsize() * self.bufsize > self.delay_cache_size):
                    if self._stopped:
                        return
                    sleep(0.1)
     
                response = self.rangefetch(start, end)
                if response is None:
                    range_queue.put((start, end))
                    continue

            try:
                data = response.read(self.bufsize)
                while data:
                    if self._stopped:
                        return
                    data_queue.put((start, data))
                    start += len(data)
                    data = response.read(self.bufsize)
            except Exception as e:
                response.close()
            else:
                response.release_conn()
            logger.debug('receive %d bytes' % start)

            if start < end + 1:
                logger.warning('retry %d-%d' % (start, end))
                range_queue.put((start, end))
                continue

getbytes = re.compile(r'^bytes=(\d*)-(\d*)(,..)?').search
getrange = re.compile(r'^bytes (\d+)-(\d+)/(\d+)').search

def spawn_later(seconds, target, *args, **kwargs):
    def wrap(*args, **kwargs):
        sleep(seconds)
        target(*args, **kwargs)
    thread.start_new_thread(wrap, args, kwargs)


def start_new_server(bind='', port=8806, first_size=None, max_size=None,
                     threads=None, scheme=None, proxy=None):
    if first_size:
        RangeFetch.first_size = first_size
    if max_size:
        RangeFetch.max_size = max_size
    if threads:
        RangeFetch.threads = threads
    if proxy:
        RangeFetch.proxy = proxy
    if scheme:
        RangeFetchHandler.scheme = scheme
    new_server = LocalTCPServer((bind, port), RangeFetchHandler)
    thread.start_new_thread(new_server.serve_forever, ())
    sleep(0.1)
    return new_server
