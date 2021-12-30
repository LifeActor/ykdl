# -*- coding: utf-8 -*-

from ._common import *


class LongzhuLive(Extractor):
    name = 'Longzhu Live (龙珠直播)'

    def prepare(self):
        info = MediaInfo(self.name, True)

        html = get_content(self.url)
        self.vid = match1(html, '(?i)"roomid":(\d+)')
        info.title = match1(html, '"title":"([^"]+)', '<title>([^>]+)<')
        info.artist = match1(html, '"Name":"([^"]+)')

        data = get_response('http://livestream.longzhu.com/live/getlivePlayurl',
                            params={
                                'roomId': self.vid,
                                'utmSr': '',
                                'platform': 'h5',
                                'device': 'pc'
                            }).json()['playLines']
        assert data, 'Live is offline!!'

        for i in data[0]['urls']:
            ext = i['ext']
            info.streams[ext] = {
                'container': ext,
                'video_profile': i['description'],
                'src' : [i['securityUrl']],
                'size': 0
            }

        return info

site = LongzhuLive()
