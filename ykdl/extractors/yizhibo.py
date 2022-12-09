# -*- coding: utf-8 -*-

from ._common import *


class Yizhibo(Extractor):
    name = 'Yizhibo (一直播)'

    def prepare_mid(self):
        return self.url[self.url.rfind('/')+1:].split('.')[0]

    def prepare(self):
        info = MediaInfo(self.name)
        info.live = True

        data = get_response(
                    'http://www.yizhibo.com/live/h5api/get_basic_live_info',
                    params={'scid': self.mid}).json()
        assert content['result'] == 1, 'Error : ' + data['result']
        data = data['data']

        info.title = data['live_title']
        info.artist = data['nickname']
        info.streams['current'] = {
            'container': 'm3u8',
            'profile': 'current',
            'src' : [data['play_url']],
            'size': Infinity
        }
        return info

site = Yizhibo()
