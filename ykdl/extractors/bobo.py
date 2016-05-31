#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.html import get_content
from ..util.match import match1
from ..simpleextractor import SimpleExtractor

from ykdl.compact import build_opener, HTTPCookieProcessor, install_opener

class BoBo(SimpleExtractor):
    name = "bobo娱乐 美女直播"

    def __init__(self):
        SimpleExtractor.__init__(self)
        self.title_pattern = '<title>([^<]+)'
        self.url_pattern = 'CDNUrl: "([^"]+)'
        cookie_handler = HTTPCookieProcessor()
        opener = build_opener(cookie_handler)
        install_opener(opener)

site = BoBo()
