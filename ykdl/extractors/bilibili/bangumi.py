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

        html = get_content(self.url)
        title = match1(html, '<h1 title="([^"]+)', '<title>([^<]+)').strip()

        if "movie" in self.url:
            aid = match1(html, 'aid=(\d+)', 'aid=\"(\d+)')
            form = {"movie_aid" : aid}
            vid = json.loads(get_content("https://bangumi.bilibili.com/web_api/get_source", data=compact_bytes(urlencode(form), 'utf-8')))["result"]["cid"]
        else:
            eid = match1(self.url, 'anime/v/(\d+)', 'play#(\d+)', 'ep(\d+)', '\d#(\d+)') or match1(html, 'anime/v/(\d+)')
            Episode_info = json.loads(get_content('http://bangumi.bilibili.com/web_api/episode/{}.json'.format(eid)))['result']['currentEpisode']
            vid = Episode_info['danmaku']
            title = title + ' ' + Episode_info['indexTitle'] + '.  ' + Episode_info['longTitle']

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
        sid = match1(html, 'var season_id = "(\d+)";')
        j_ = get_content("http://bangumi.bilibili.com/jsonp/seasoninfo/{}.ver".format(sid))
        s_data = json.loads(j_)
        urls = [e['webplay_url'] for e in sorted(s_data['result']['episodes'], key=lambda e: e['index'])]
        return urls

site = BiliBan()
