#!/usr/bin/env python

from ..common import *
from ..simpleextractor import SimpleExtractor

class Magisto(SimpleExtractor):
    name = "Magisto"

    def __init__(self):
        SimpleExtractor.__init__(self)
        self.url_pattern = '<source type="[^"]+" src="([^"]*)"'

    def get_title(self):
        title1 = r1(r'<meta name="twitter:title" content="([^"]*)"', self.html)
        title2 = r1(r'<meta name="twitter:description" content="([^"]*)"', self.html)
        video_hash = r1(r'http://www.magisto.com/video/([^/]+)', self.url)
        self.title = "%s %s - %s" % (title1, title2, video_hash)

site = Magisto()
download = site.download_by_url
download_playlist = playlist_not_supported('magisto')
