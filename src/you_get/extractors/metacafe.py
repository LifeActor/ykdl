#!/usr/bin/env python

from ..common import *
import urllib.error
from urllib.parse import unquote
from ..simpleextractor import SimpleExtractor
import re

class Metacafe(SimpleExtractor):
    name = "Metacafe"

    def __init__(self, *args):
        SimpleExtractor.__init__(self, *args)
        self.title_pattern = '<meta property="og:title" content="([^"]*)"'

    def l_assert(self):
        assert re.match(r'http://www.metacafe.com/watch/\w+', self.url)

    def get_url(self):
        url_raw = match1(html, '&videoURL=([^&]+)')
        self.v_url = [unquote(url_raw)]

site = Metacafe()
download = site.download_by_url
download_playlist = playlist_not_supported('metacafe')
