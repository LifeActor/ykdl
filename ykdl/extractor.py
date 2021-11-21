from logging import getLogger
from urllib.request import HTTPCookieProcessor

from .videoinfo import VideoInfo
from .util.http import (add_default_handler, install_default_handlers,
                        remove_default_handler)


class VideoExtractor:

    cookiejar = None

    def __init__(self):
        self.logger = getLogger(self.name)

    def parser(self, url):
        self.url = None
        self.vid = None
        if isinstance(url, str) and url.startswith('http'):
            self.url = url
            if self.list_only():
                return self.parser_list(url)
        else:
            self.vid= url

        info = self.prepare()
        info.sort()
        return info

    def parser_list(self, url):
        self.url = url
        self._is_list = True
        video_list = self.prepare_list()
        #print(video_list)
        if not video_list:
            print(video_list)
            raise NotImplementedError(
                    'playlist not support for {self.name} with url: {self.url}'
                    .format(**vars()))
        for video in video_list:
            if isinstance(video, VideoInfo):
                info = video
            else:
                info = self.parser(video)
            if info:
                info.sort()
                yield info

    def prepare(self):
        '''
        this API is to do real job to get source URL, or site and VID
        sometimes title
        MUST override!!
        '''
        pass

    def prepare_list(self):
        '''
        this API is to do real job to get source URL, or site and VID
        sometimes title
        MUST override!!
        '''
        pass

    @property
    def is_list(self):
        try:
            return self._is_list
        except AttributeError:
            self._is_list = self.list_only()
            return self._is_list

    def list_only(self):
        '''
        this API is to check if only the list informations is included
        if true, go to parser list mode
        MUST override!!
        '''
        pass

    def install_cookie(self):
        '''Install HTTPCookieProcessor to default opener.'''
        if self.cookiejar is None:
            handler = HTTPCookieProcessor()
            add_default_handler(handler)
            install_default_handlers()
            self.cookiejar = handler.cookiejar

    def uninstall_cookie(self):
        '''Uninstall HTTPCookieProcessor from default opener.'''
        if self.cookiejar:
            remove_default_handler(HTTPCookieProcessor)
            install_default_handlers()
            self.cookiejar = None

    def get_cookie(self, domain, path, name):
        '''Return specified cookie in existence, or None.

        MUST call self.install_cookie() before use.
        '''
        try:
            return self.cookiejar._cookies[domain][path][name]
        except KeyError:
            pass

    def get_cookies(self, domain=None, path=None, name=None):
        '''Get cookies in existence.
        No param (None) get all, mismatch param get empty.

        MUST call self.install_cookie() before use.
        '''
        if name and path and domain:
            return [self.get_cookie(domain, path, name)]
        cookies = []
        c = self.cookiejar._cookies
        if domain is None:
            dl = c.values()
        else:
            d = c.get(domain)
            dl = d and [d] or []
        for d in dl:
            if path is None:
                pl = d.values()
            else:
                p = d.get(path)
                pl = p and [p] or []
            for p in pd:
                if name is None:
                    cookies.extend(p.values())
                else:
                    n = p.get(name)
                    if n:
                        cookies.append(n)
        return cookies


