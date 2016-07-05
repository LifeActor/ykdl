#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.html import get_content
from ..embedextractor import EmbedExtractor
from ..util.match import match1

import re
import json

class Tudou(EmbedExtractor):
    name = "土豆 (tudou)"

    def prepare(self):

        if re.search('acfun', self.url):
            self.video_url.append(('acfun', self.url))
            return

        html = get_content(self.url)
        vcode = match1(html, 'vcode\s*[:=]\s*\'([^\']+)\'')
        if vcode:
            self.video_info = ('youku', vcode)
        else:
            vid = match1(html, 'iid\s*[:=]\s*(\d+)')
            if vid:
                self.video_info = ('tdorig', vid)

    def prepare_playlist(self):
        html = get_content(self.url)
        lcode = match1(html, "lcode:\s*'([^']+)'")
        plist_info = json.loads(get_content('http://www.tudou.com/crp/plist.action?lcode=' + lcode))
        self.video_info_list = [('tdorig',item['iid']) for item in plist_info['items'] if 'iid' in item]

site = Tudou()
