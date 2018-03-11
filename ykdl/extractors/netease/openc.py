#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.simpleextractor import SimpleExtractor
from ykdl.util.match import match1

class OpenC(SimpleExtractor):
    name = u"网易公开课 (163 openCourse)"

    def __init__(self):
        SimpleExtractor.__init__(self)
        self.url_pattern = 'appsrc : ([^ ]+)'
        self.title_pattern = 'title : ([^ ]+)'

    def get_url(self):
        url = match1(self.html, self.url_pattern)
        self.v_url = [url[2:-5]]

site = OpenC()
