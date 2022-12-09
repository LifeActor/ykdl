# -*- coding: utf-8 -*-

from .._common import *
from .util import get_h5enc, ub98484234


class DouyutvVideo(Extractor):
    name = '斗鱼视频 (DouyuTV)'

    profile_2_id = {
         'super': 'OG',  # Need Login
          'high': 'TD',
        'normal': 'HD'
    }

    def prepare_mid(self):
        return match1(self.url, 'show/(\w+)')

    def prepare(self):
        info = MediaInfo(self.name)

        if self.url is None or 'vmobile' in self.url:
            self.url = 'https://v.douyu.com/show/' + self.mid

        html = get_content(self.url)
        info.title = match1(html, 'title>(.+?)-斗鱼视频<')
        vid = match1(html, '"point_id":\s?(\d+)')
        assert vid, "can't find video!!!"

        js_enc = get_h5enc(html, vid)
        params = {'vid': self.mid}
        ub98484234(js_enc, vid, self.logger, params)

        add_header('Referer', self.url)
        data = get_response('https://v.douyu.com/api/stream/getStreamUrl',
                            {'Cookie': 'dy_did=' + params['did']},
                            data=params).json()
        assert data['error'] == 0, data

        for stream_profile, st_date in data['data']['thumb_video'].items():
            if not st_date:
                continue
            stream_id = self.profile_2_id[stream_profile]
            info.streams[stream_id] = {
                'container': 'm3u8',
                'profile': stream_profile,
                'src': [st_date['url']]
            }

        return info

site = DouyutvVideo()
