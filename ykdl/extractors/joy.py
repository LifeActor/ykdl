# -*- coding: utf-8 -*-

from ._common import *


class Joy(Extractor):

    name = '激动网 (Joy)'

    def prepare(self):
        info = MediaInfo(self.name)
        if not self.vid:
            self.vid = match1(self.url, 'resourceId=([0-9]+)')

        data= get_response('https://api.joy.cn/v1/video',
                           params={'id': self.vid}).json()
        assert data['code'] > 0, data['message']
        data = data['data']

        info.title = data['title']
        url = data['res_url']
        _, ext, _ = url_info(url)

        info.streams['current'] = {
            'container': ext,
            'video_profile': 'current',
            'src': [url]
        }
        return info

site = Joy()
