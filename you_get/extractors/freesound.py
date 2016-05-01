#!/usr/bin/env python

from ..simpleextractor import SimpleExtractor


class Freesound(SimpleExtractor):
    name = "Freesound"

    def __init__(self):
        SimpleExtractor.__init__(self)
        self.title_pattern = '<meta property="og:title" content="([^"]*)"'
        self.url_pattern = '<meta property="og:audio" content="([^"]*)"'

site = Freesound()
