#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.match import match1
from ..simpleextractor import SimpleExtractor

class Magisto(SimpleExtractor):
    name = "Magisto"

    def __init__(self):
        SimpleExtractor.__init__(self)
        self.url_pattern = '<source type="[^"]+" src="([^"]*)"'

    def get_title(self):
        title1 = match1(self.html, '<meta name="twitter:title" content="([^"]*)"')
        title2 = match1(self.html, '<meta name="twitter:description" content="([^"]*)"')
        video_hash = match1( self.url, 'http://www.magisto.com/video/([^/]+)')
        self.title = "%s %s - %s" % (title1, title2, video_hash)

site = Magisto()
