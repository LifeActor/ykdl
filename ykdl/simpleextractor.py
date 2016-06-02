#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .util.html import get_content, fake_headers, url_info
from .util.match import match1
from .extractor import VideoExtractor

class SimpleExtractor(VideoExtractor):

    name = "SimpleExtractor"

    def __init__(self):
        VideoExtractor.__init__(self)

        self.html = ''

        self.title_pattern = ''

        self.url_pattern = ''

        self.artist_pattern = ''

        self.headers = fake_headers

    def get_title(self):
        if self.title_pattern:
            self.title = match1(self.html, self.title_pattern)

    def get_artist(self):
        if self.artist_pattern:
            self.artist = match1(self.html, self.artist_pattern)

    def get_url(self):
        if self.url_pattern:
            self.v_url = [match1(self.html, self.url_pattern)]

    def get_info(self):
        size=0
        ext=''
        for u in self.v_url:
            _, ext, temp = url_info(u)
            size += temp
        return ext, size

    def l_assert(self):
        pass

    def prepare(self):
        self.l_assert()
        self.html = get_content(self.url, headers=self.headers)
        self.get_title()
        self.get_artist()
        self.get_url()
        ext, size = self.get_info()
        self.stream_types.append('current')
        self.streams['current'] = {'container': ext, 'src': self.v_url, 'size' : size}
