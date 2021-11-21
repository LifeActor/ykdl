# -*- coding: utf-8 -*-

from ._common import *


SECKEY = 'RTYDFkHAL$#%^tsf_)(*^Gd%$'

class Chushou(VideoExtractor):
    name = 'Chushou Live (触手直播)'

    def prepare(self):
        info = VideoInfo(self.name, True)
        self.vid = match1(self.url, '(\d+).htm')

        t = get_content('https://chushou.tv/timestamp/get.htm')
        params = [
            ('', SECKEY),
            ('_t', t),
            ('protocols' , '1,2'),
            ('roomId' , self.vid)
        ]
        sign = hash.md5(urlencode(params)[1:])
        del params[0]
        params.append(('_sign', sign))

        data = get_content('https://chushou.tv/live-room/get-play-url.htm',
                           params=params).json()
        assert data['code'] == 0, data['message']

        info.stream_types.append('current')
        info.streams['current'] = {
            'container': 'flv',
            'video_profile': 'current',
            'src' : [data['data'][0]['shdPlayUrl']],
            'size': float('inf')
        }

        return info

site = Chushou()
