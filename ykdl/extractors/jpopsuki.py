#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..simpleextractor import SimpleExtractor

class JPopsuki(SimpleExtractor):
    name = "JPopsuki"
    def __init__(self):
        SimpleExtractor.__init__(self)
        self.title_pattern = '<meta name="title" content="([^"]*)"'

    def get_url(self):
        self.v_url = ["http://jpopsuki.tv{}".format(match1(self.html, '<source src="([^"]*)"'))]

site = JPopsuki()
