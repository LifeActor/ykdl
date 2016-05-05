#!/usr/bin/env python3

from ..util.html import get_content
from ..util.match import match1
from ..simpleextractor import SimpleExtractor
from urllib import request

class BoBo(SimpleExtractor):
    name = "bobo娱乐 美女直播"

    def __init__(self):
        SimpleExtractor.__init__(self)
        self.title_pattern = '<title>([^<]+)'
        self.url_pattern = 'CDNUrl: "([^"]+)'
        cookie_handler = request.HTTPCookieProcessor()
        opener = request.build_opener(cookie_handler)
        request.install_opener(opener)

site = BoBo()
