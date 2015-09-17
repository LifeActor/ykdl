#!/usr/bin/env python

from ..common import *
from ..simpleextractor import SimpleExtractor
from urllib.parse import unquote

class Miaopai(SimpleExtractor):
    name = "微博秒拍 (Miaopai)"


    def __init__(self):
        SimpleExtractor.__init__(self)
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

site = Miaopai()
download = site.download_by_url
download_playlist = playlist_not_supported('miaopai')
