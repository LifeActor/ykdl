# -*- coding: utf-8 -*-

from ._common import *


class Joy(Extractor):

    name = '激动网 (Joy)'

    def prepare_mid(self):
        return match1(self.url, 'resourceId=([0-9]+)')

    def prepare(self):
        info = MediaInfo(self.name)

        data= get_response('https://api.joy.cn/v1/video',
                           params={'id': self.mid}).json()
        assert data['code'] > 0, data['message']
        data = data['data']

        info.title = data['title']
        url = data['res_url']
        _, ext, _ = url_info(url)

        info.streams['current'] = {
            'container': ext,
            'profile': 'current',
            'src': [url]
        }
        return info

site = Joy()
