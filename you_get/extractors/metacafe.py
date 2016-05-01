#!/usr/bin/env python

from ..util.match import match1
from urllib.parse import unquote
from ..simpleextractor import SimpleExtractor
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
        self.v_url = [unquote(url_raw)]

site = Metacafe()
