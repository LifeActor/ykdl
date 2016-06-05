#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.match import match1
from ..simpleextractor import SimpleExtractor

from ykdl.compact import compact_unquote
import re

class Metacafe(SimpleExtractor):
    name = "Metacafe"

    def __init__(self):
        SimpleExtractor.__init__(self)
        self.title_pattern = '<meta property="og:title" content="([^"]*)"'

    def l_assert(self):
        assert re.match(r'http://www.metacafe.com/watch/\w+', self.url)

    def get_url(self):
        url_raw = match1(html, '&videoURL=([^&]+)')
        self.v_url = [compact_unquote(url_raw)]

site = Metacafe()
