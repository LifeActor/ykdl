#!/usr/bin/env python

from ..common import *
from ..simpleextractor import SimpleExtractor
from urllib.parse import unquote

class Weibo(SimpleExtractor):
    name = "微博秒拍 (Weibo)"


    def __init__(self, *args):
        SimpleExtractor.__init__(self, *args)
        self.title_pattern = '<meta name="description" content="(.*?)\"\W'

    def get_url(self):
        url_raw = match1(self.html, 'flashvars="list=([^"]+)')
        self.v_url = [unquote(url_raw)]

    def get_info(self):
        """
        sometime url_info will fail
        but url is availible
        so use fake
        """
        return 'mp4', 1

site = Weibo()
download = site.download_by_url
download_playlist = playlist_not_supported('Weibo')
