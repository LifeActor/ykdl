#!/usr/bin/env python3

from ..embedextractor import EmbedExtractor

class Baidu(EmbedExtractor):
    name = 'Baidu (百度)'

    def prepare(self):

        if self.url.startswith("http://music"):
            self.video_info.append(("baidumusic", self.url))

    def prepare_playlist(self):

        if self.url.startswith("http://music"):
            self.video_info.append(("baidumusic", self.url))

site = Baidu()
