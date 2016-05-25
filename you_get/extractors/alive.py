#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..simpleextractor import SimpleExtractor

class Alive(SimpleExtractor):
    name = "Alive"

    def __init__(self):
        SimpleExtractor.__init__(self)
        self.title_pattern = '<meta property="og:title" content="([^"]+)"'
        self.url_pattern = 'file: "(http://alive[^"]+)"'

site = Alive()
