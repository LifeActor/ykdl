#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..simpleextractor import SimpleExtractor
from ykdl.util.html import add_header, get_content
from ykdl.util.match import match1

class Weibo(SimpleExtractor):
    name = u"微博秒拍 (Weibo)"

    def __init__(self):
        SimpleExtractor.__init__(self)
        add_header('User-Agent', 'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36')
        self.url_pattern = '(?:data-url|video_src|controls src)=(?:\"|\')([^\"\']+)'
        self.title_pattern = '<title>([^<]+)</'

    def l_assert(self):
        self.url = self.url.replace('%3A', ':')
        fid = match1(self.url, r'\?fid=(\d{4}:\w+)')
        if fid is not None:
            self.url = 'http://video.weibo.com/show?fid={}&type=mp4'.format(fid)
        elif '/p/230444' in self.url:
            fid = match1(url, r'/p/230444(\w+)')
            self.url = 'http://video.weibo.com/show?fid=1034:{}&type=mp4'.format(fid)
        else:
            html = get_content(self.url)
            url = match1(html, r'"page_url"\s*:\s*"([^"]+)"')
            assert url, 'No url match'
            self.url = url
            self.l_assert()

    def get_title(self):
        self.title = SimpleExtractor.get_title(self) or self.name

site = Weibo()
