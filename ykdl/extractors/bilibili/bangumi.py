# -*- coding: utf-8 -*-

from .._common import *
from .bilibase import BiliBase, sign_api_url


APPKEY = '84956560bc028eb7'
SECRETKEY = '94aba54af9065f71de72f5508f1cd42e'
api_url = 'https://bangumi.bilibili.com/player/web_api/v2/playurl'

class BiliBan(BiliBase):
    name = '哔哩哔哩 番剧 (Bilibili Bangumi)'

    def list_only(self):
        return '/play/ss' in self.url

    def get_page_info(self):
        html = get_content(self.url)
        date = json.loads(match1(html, '__INITIAL_STATE__=({.+?});'))
        vid = date['epInfo']['cid']
        mediaInfo = date['mediaInfo']
        self.seasonType = mediaInfo.get('ssType')
        title = date.get('h1Title') or \
                match1(html, '<title>(.+?)[_-]\w+[_-]bilibili[_-]哔哩哔哩<')
        upInfo = mediaInfo.get('upInfo')
        artist = upInfo and upInfo.get('name')

        return vid, title, artist

    def get_api_url(self, qn):
        params_str = urlencode([
            ('appkey', APPKEY),
            ('cid', self.vid),
            ('module', 'bangumi'),
            ('platform', 'html5'),
            ('player', 1),
            ('qn', qn),
            ('season_type', self.seasonType)
        ])
        return sign_api_url(api_url, params_str, SECRETKEY)

    def prepare_list(self):
        html = get_content(self.url)
        eplist = matchall(html, '"epList":(\[.*?\])')
        if eplist:
            eplist = [match1(ep, '"(?:ep_)?id":(\d+),') for ep in eplist]
            return ['https://www.bilibili.com/bangumi/play/ep' + eid
                    for eid in eplist if eid]

site = BiliBan()
