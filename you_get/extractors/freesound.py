#!/usr/bin/env python


from ..common import *
from ..simpleextractor import SimpleExtractor


class Freesound(SimpleExtractor):
    name = "Freesound"

    def __init__(self, *args):
        SimpleExtractor.__init__(self, *args)
        self.title_pattern = '<meta property="og:title" content="([^"]*)"'
        self.url_pattern = '<meta property="og:audio" content="([^"]*)"'

site = Freesound()
download = site.download_by_url
download_playlist = playlist_not_supported('freesound')
