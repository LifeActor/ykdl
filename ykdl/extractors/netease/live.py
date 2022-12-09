# -*- coding: utf-8 -*-

from .._common import *


class NeteaseLive(Extractor):
    name = '网易直播 (163)'

    def prepare_mid(self):
        return match1(self.url, 'room/(\d+)')

    def prepare(self):
        info = MediaInfo(self.name, True)

        data = get_response(
            'https://data.live.126.net/liveAll/{self.mid}.json'.format(**vars()),
            params={'tt': int(time.time() * 1000)}
        ).json()
        assert 'liveVideoUrl' in data, 'live video is offline'

        info.title = data['roomName']
        try:
            info.artist = data['sourceinfo']['tname']
        except KeyError:
            pass
        info.duration = duration = data.get('duration')
        info.add_comment = data['channal']['name']

        url = data['liveVideoUrl']
        info.streams['current'] = {
            'container': url.split('.')[-1],
            'profile': 'current',
            'src': [url],
            not duration and 'size': Infinity
        }
        return info

site = NeteaseLive()
