#!/usr/bin/env python

from ..common import *
import urllib.error
from urllib.parse import unquote
from ..simpleextractor import SimpleExtractor
import re

class Metacafe(SimpleExtractor):
    name = "Metacafe"

    def __init__(self):
        SimpleExtractor.__init__(self)
        self.title_pattern = '<meta property="og:title" content="([^"]*)"'
        self.url_pattern = '&videoURL=([^&]+)'

    def l_assert(self):
        assert re.match(r'http://www.metacafe.com/watch/\w+', self.url)

site = Metacafe()
download = site.download_by_url
download_playlist = playlist_not_supported('metacafe')
