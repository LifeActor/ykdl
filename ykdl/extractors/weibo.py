#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..simpleextractor import SimpleExtractor
from ykdl.util.html import add_header

class Weibo(SimpleExtractor):
    name = u"微博秒拍 (Weibo)"

    def __init__(self):
        SimpleExtractor.__init__(self)
        add_header('User-Agent', 'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36')
        self.url_pattern = '<video src="(.*?)\"\W'
        self.title_pattern = '<meta name="description" content="([\s\S]*?)\"\W'

    def l_assert(self):
        self.url = 'http://video.weibo.com/show?fid=1034:' + self.url[-32:] + '&type=mp4'

    def get_title(self):
        self.title = SimpleExtractor.get_title(self) or self.name

site = Weibo()
