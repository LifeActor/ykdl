#!/usr/bin/env python

from ..common import *
from ..simpleextractor import SimpleExtractor

class Iqilu(SimpleExtractor):
    name = "齐鲁网 (iqilu)"

    def __init__(self, *args):
        SimpleExtractor.__init__(self, *args)
        self.title_pattern = '<meta name="description" content="(.*?)\"\W'
        self.url_pattern = "<input type='hidden' id='playerId' url='(.+)'"

    def l_assert(self):
        assert re.match(r'http://v.iqilu.com/\w+', self.url)

site = Iqilu()
download = site.download_by_url
download_playlist = playlist_not_supported('iqilu')
