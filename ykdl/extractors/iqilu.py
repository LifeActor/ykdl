# -*- coding: utf-8 -*-

from ._common import *


class Iqilu(SimpleExtractor):
    name = '齐鲁网 (iqilu)'

    def init(self):
        self.title_pattern = '<meta name="description" content="(.+?)"\W'
        self.artist_pattern = '<title>.+?_([^_]+?频道)_山东网络台_齐鲁网</title>'
        self.url_pattern = '"mp4-wrapper"[^"]+"(http[^"]+)"'

    def l_assert(self):
        assert match(self.url, 'https?://v\.iqilu\.com/\w+')

    def reprocess(self):
        self.info.title = '[{self.info.artist}] {self.info.title}'.format(**vars())

site = Iqilu()
