# -*- coding: utf-8 -*-

from .._common import *
from .sohubase import SohuBase


class TvSohu(SohuBase):
    name = '搜狐视频 (TvSohu)'

    apiurl = 'http://hot.vrs.sohu.com/vrs_flash.action'
    apiparams = {'vid': ''}

    def list_only(self):
        return bool(match(self.url, 'tv.sohu.com/s\d{4}/[a-z]'))

    def prepare_list(self):
        html = get_content(self.url)
        plid = match1(html, r'\bplaylistId\s*=\s*["\']?(\d+)')
        data = get_response('https://pl.hd.sohu.com/videolist',
                            params={
                                'playlistid': plid,
                                'order': 0,
                                'cnt': 1,
                                'withLookPoint': 1,
                                'preVideoRule': 3,
                                'ssl': 1,
                                'callback': '__get_videolist',
                                '_': int(time.time() * 1000)
                            }).json()
        mids = [str(v['vid']) for v in data['videos']]
        mid = not self.list_only and self.mid or None
        self.set_index(mid, mids)
        return mids

site = TvSohu()
