#!/usr/bin/env python

from .common import *
from .extractor import VideoExtractor

class SimpleExtractor(VideoExtractor):

    name = "SimpleExtractor"

    def __init__(self):
        VideoExtractor.__init__(self)

        self.html = ''

        self.title_pattern = ''

        self.url_pattern = ''

        self.faker = False

    def get_title(self):
        self.title = match1(self.html, self.title_pattern)

    def get_url(self):
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

    def prepare(self, **kwargs):
        assert self.url
        self.l_assert()
        self.html = get_html(self.url, faker = self.faker)
        self.get_title()
        self.get_url()
        ext, size = self.get_info()
        self.stream_types.append('current')
        self.streams['current'] = {'container': ext, 'src': self.v_url, 'size' : size}

    def download_by_vid(self, **kwargs):
        pass
