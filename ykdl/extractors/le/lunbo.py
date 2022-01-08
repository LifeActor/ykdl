# -*- coding: utf-8 -*-

from .._common import *


class LeLunbo(Extractor):
    name = 'Le Lunbo (乐视轮播)'

    stream_2_id_profile = {
        'flv_1080p3m': ['BD', '1080p'],
        'flv_1080p'  : ['BD', '1080p'],
        'flv_1300'   : ['TD',  '超清'],
        'flv_1000'   : ['HD',  '高清'],
        'flv_720p'   : ['SD',  '标清'],
        'flv_350'    : ['LD',  '流畅']
    }

    def prepare(self):
        info = MediaInfo(self.name, True)
        if not self.vid:
            self.vid = match1(self.url, 'channel=([\d]+)')

        live_data = get_response(
                'http://player.pc.le.com/player/startup_by_channel_id/1001/'
                + self.vid,
                params={'host': 'live.le.com'}).json()
        info.title = live_data['channelName']

        for st in live_data['streams']:
            stream, profile = self.stream_2_id_profile[st['rateType']]
            data = get_response(st['streamUrl'],
                                params={
                                    'format': 1,
                                    'expect': 2,
                                    'termid': 1,
                                    'platid': 10,
                                    'playid': 1,
                                    'sign': 'live_web',
                                    'splatid': 1001,
                                    'vkit': 20161017,
                                    'station': self.vid
                                }).json()
            src = data['location']
            info.streams[stream] = {
                'container': 'm3u8',
                'video_profile': profile,
                'size' : float('inf'),
                'src' : [src]
            }

        return info

site = LeLunbo()
