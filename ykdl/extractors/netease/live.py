# -*- coding: utf-8 -*-

from .._common import *


class NeteaseLive(VideoExtractor):
    name = '网易直播 (163)'

    def prepare(self):
        info = VideoInfo(self.name, True)

        if self.vid is None:
            self.vid = match1(self.url, 'room/(\d+)')

        tt = int(time.time() * 1000)
        url = 'https://data.live.126.net/liveAll/{self.vid}.json?{tt}'.format(**vars())
        data = get_response(url).json()
        assert 'liveVideoUrl' in data, 'live video is offline'

        info.title = data['roomName']
        try:
            info.artist = data['sourceinfo']['tname']
        except KeyError:
            pass

        url = data['liveVideoUrl']
        info.stream_types.append('current')
        info.streams['current'] = {
            'container': url.split('.')[-1],
            'video_profile': 'current',
            'src': [url],
            'size': 0
        }
        return info

site = NeteaseLive()
