#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_location, get_content
from ykdl.util.match import match1
from ykdl.compact import compact_bytes, urlencode

import json
import time
import hashlib

from .bilibase import BiliBase

SEC2 = '9b288147e5474dd2aa67085f716c560d'
bangumi_api_url = 'http://bangumi.bilibili.com/player/web_api/playurl?'

class BiliBan(BiliBase):
    name = u'哔哩哔哩 番剧 (Bilibili Bangumi)'

    def get_vid_title(self):
        if not 'bangumi' in self.url:
            self.url = get_location(self.url)

        html = get_content(self.url)
        title = match1(html, '<h1 title="([^"]+)', '<title>([^<]+)').strip()

        vid = match1(html, '\"cid\":(\d+)')

        return vid, title

    def get_api_url(self, q):
        if "movie" in self.url:
            mod = "movie"
        else:
            mod = "bangumi"
        ts = str(int(time.time()))
        params_str = 'cid={}&module={}&player=1&quality={}&ts={}'.format(self.vid, mod, q, ts)
        chksum = hashlib.md5(compact_bytes(params_str + SEC2, 'utf8')).hexdigest()
        return bangumi_api_url + params_str + '&sign=' + chksum

    def prepare_list(self):
        html = get_content(self.url)
        sid = match1(html, 'var season_id = "(\d+)";')
        j_ = get_content("https://bangumi.bilibili.com/jsonp/seasoninfo/{}.ver".format(sid))[19:-2]
        s_data = json.loads(j_)
        urls = [e['webplay_url'] for e in sorted(s_data['result']['episodes'], key=lambda e: e['index'])]
        return urls

site = BiliBan()
