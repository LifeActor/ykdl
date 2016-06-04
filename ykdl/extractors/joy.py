#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.html import get_content, url_info
from ..util.match import match1, matchall
from ..extractor import VideoExtractor

class Joy(VideoExtractor):

    name = u'激动网 (Joy)'


    def prepare(self):

        if not self.vid:
            self.vid = match1(self.url, 'resourceId=([0-9]+)')
        if not self.url:
            self.url = "http://www.joy.cn/video?resourceId={}".format(self.vid)

        html= get_content(self.url)

        self.title = match1(html, '<meta content=\"([^\"]+)')

        url = matchall(html, ['<source src=\"([^\"]+)'])[3]

        _, ext, size = url_info(url)

        self.stream_types.append('current')
        self.streams['current'] = {'container': ext, 'src': [url], 'size': size }

site = Joy()
