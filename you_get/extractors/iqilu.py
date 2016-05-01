#!/usr/bin/env python

from ..simpleextractor import SimpleExtractor
import re

class Iqilu(SimpleExtractor):
    name = "齐鲁网 (iqilu)"

    def __init__(self):
        SimpleExtractor.__init__(self)
        self.title_pattern = '<meta name="description" content="(.*?)\"\W'
        self.url_pattern = "<input type='hidden' id='playerId' url='(.+)'"

    def l_assert(self):
        assert re.match(r'http://v.iqilu.com/\w+', self.url)

site = Iqilu()
