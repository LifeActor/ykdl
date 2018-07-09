#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_location, get_content
from ykdl.util.match import match1, matchall
from ykdl.compact import compact_bytes, urlencode

import json

from .bilibase import BiliBase, sign_api_url


SECRETKEY = '9b288147e5474dd2aa67085f716c560d'
api_url = 'https://bangumi.bilibili.com/player/web_api/playurl'

class BiliBan(BiliBase):
    name = u'哔哩哔哩 番剧 (Bilibili Bangumi)'

    def get_vid_title(self):

        html = get_content(self.url)
        title = match1(html, '<h1 title="([^"]+)', '<title>([^<]+)').strip()
        vid = match1(html, '"cid":(\d+)', 'cid=(\d+)', 'cid="(\d+)')

#        eid = match1(self.url, 'anime/v/(\d+)', 'play#(\d+)', 'ep(\d+)', '\d#(\d+)') or match1(html, 'anime/v/(\d+)')
#        if eid:
#            Episode_info = json.loads(get_content('http://bangumi.bilibili.com/web_api/episode/{}.json'.format(eid)))['result']
#            vid = Episode_info['currentEpisode']['danmaku']
#            title = Episode_info['season']['title'] + ' ' + Episode_info['currentEpisode']['indexTitle'] + '.  ' + Episode_info['currentEpisode']['longTitle']
#        else:
#            vid = match1(html, 'cid=(\d+)', 'cid="(\d+)', '"cid":(\d+)')

        return vid, title

    def get_api_url(self, qn):
        params_str = 'cid={}&module=bangumi&player=1&qn={}'.format(self.vid, qn)
        return sign_api_url(api_url, params_str, SECRETKEY)

    def prepare_list(self):
        html = get_content(self.url)
        video_list = matchall(html, [',"ep_id":(\d+),'])
        if video_list:
            del video_list[0]
            return ['https://www.bilibili.com/bangumi/play/ep{}'.format(eid) for eid in video_list]
#        sid = match1(html, 'var season_id = "(\d+)";') or match1(self.url, "anime/(\d+)")
#        j_ = get_content("https://bangumi.bilibili.com/jsonp/seasoninfo/{}.ver?callback=seasonListCallback".format(sid))[19:-2]
#        s_data = json.loads(j_)
#        urls = [e['webplay_url'] for e in sorted(s_data['result']['episodes'], key=lambda e: int(e['index']))]
#        return urls

site = BiliBan()
