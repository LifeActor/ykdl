#!/usr/bin/env python

from ..common import *
from ..simpleextractor import SimpleExtractor
from urllib.parse import unquote

class Weibo(SimpleExtractor):
    name = "微博秒拍 (Weibo)"


    def __init__(self, *args):
        SimpleExtractor.__init__(self, *args)
        self.title= self.name
        self.headers['Cookie'] = 'SUB=_2AkMhFM7jf8NhqwJRmPgSxGjgbo9-wwHEiebDAHzsJxJjHn8Y7T9S2ly7eBeF6R30KmjZVAl34ha-NA..'

    def get_url(self):
        url_raw = match1(self.html, 'file=([^"]+)')
        self.v_url = [unquote(url_raw[:-1])]

site = Weibo()
download = site.download_by_url
download_playlist = playlist_not_supported('Weibo')
