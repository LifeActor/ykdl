#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_location, get_content
from ykdl.util.match import match1, matchall
from ykdl.compact import compact_bytes, urlencode

import json

from .bilibase import BiliBase, sign_api_url


APPKEY = '84956560bc028eb7'
SECRETKEY = '94aba54af9065f71de72f5508f1cd42e'
api_url = 'https://bangumi.bilibili.com/player/web_api/v2/playurl'

class BiliBan(BiliBase):
    name = u'哔哩哔哩 番剧 (Bilibili Bangumi)'

    def list_only(self):
        return '/play/ss' in self.url

    def get_page_info(self):
        html = get_content(self.url)
        date = json.loads(match1(html, '__INITIAL_STATE__=({.+?});'))
        title = date['h1Title']
        vid = date['epInfo']['cid']
        mediaInfo = date['mediaInfo']
        artist = mediaInfo['upInfo']['name']
        self.seasonType = mediaInfo['ssType']

        return vid, title, artist

    def get_api_url(self, qn):
        params_str = 'appkey={}&cid={}&module=bangumi&player=1&qn={}&season_type={}'.format(APPKEY, self.vid, qn, self.seasonType)
        return sign_api_url(api_url, params_str, SECRETKEY)

    def prepare_list(self):
        html = get_content(self.url)
        eplist = match1(html, '"epList":(\[.+?\])')
        if eplist:
            eplist = matchall(eplist, [',"id":(\d+),'])
            return ['https://www.bilibili.com/bangumi/play/ep{}'.format(eid) for eid in eplist]

site = BiliBan()
