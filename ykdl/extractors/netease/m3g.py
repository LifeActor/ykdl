# -*- coding: utf-8 -*-

from .._common import *


class m3g(SimpleExtractor):
    name = '网易手机网 (163 3g)'

    def init(self):
        self.url_patterns = ['"contentUrl":"([^"]+)"', '<video\s+data-src="([^"]+)"']
        self.title_pattern = 'class="title">(.+?)</'

    def get_url(self):
        if self.url_patterns:
            v_url = []
            for url in matchall(self.html, *self.url_patterns):
                if url[:2] == '//':
                    url = 'http:' + url
                if url not in v_url:
                    v_url.append(url)
            self.v_url = v_url

site = m3g()
