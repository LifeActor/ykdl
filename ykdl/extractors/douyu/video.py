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

    def prepare(self):
        info = MediaInfo(self.name)
        pid = match1(self.url, 'show/(.*)')
        if 'vmobile' in self.url:
            self.url = 'https://v.douyu.com/show/' + pid

        html = get_content(self.url)
        info.title = match1(html, 'title>(.+?)_斗鱼视频 - 最6的弹幕视频网站<')
        self.vid = match1(html, '"point_id":\s?(\d+)')

        js_enc = get_h5enc(html, self.vid)
        params = {'vid': pid}
        ub98484234(js_enc, self, params)

        add_header('Referer', self.url)
        video_data = get_response('https://v.douyu.com/api/stream/getStreamUrl',
                                  {'Cookie': 'dy_did=' + params['did']},
                                  data=params).json()
        assert video_data['error'] == 0, video_data

        for video_profile, st_date in video_data['data']['thumb_video'].items():
            if not st_date:
                continue
            stream = self.profile_2_id[video_profile]
            info.streams[stream] = {
                'container': 'm3u8',
                'video_profile': video_profile,
                'src' : [st_date['url']],
                'size': 0
            }

        return info

site = DouyutvVideo()
