# -*- coding: utf-8 -*-

from ._common import *


class ZYLive(SimpleExtractor):
    name = 'ZhangYu Live (章鱼直播)'

    def init(self):
        self.headers['User-Agent'] = (
                    'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) '
                    'AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 '
                    'Mobile/9A334 Safari/7534.48.3')
        self.live = True
        self.title_pattern = '<title>([^<]+)'
        self.url_pattern = "<video _src='([^']+)"
        self.artist_pattern = 'videoTitle = "([^"]+)'

site = ZYLive()
