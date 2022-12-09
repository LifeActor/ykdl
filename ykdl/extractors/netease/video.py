# -*- coding: utf-8 -*-

from .._common import *


class NeteaseVideo(Extractor):
    name = '网易视频 (163)'

    def prepare_mid(self):
        return match1(self.url, '(\w+)\.html')

    def prepare(self):
        info = MediaInfo(self.name)

        data = get_response('https://so.v.163.com/v6/video/videodetail.do',
                            params={
                               'vid': self.mid,
                               'adapter': 1
                            }).json()
        assert data['code'] == 1, data['msg']
        data = data['data']

        info.title = data['title']
        info.artist = data.get('username')
        info.add_comment(data['keywords'])
        info.streams['current'] = {
            'container': 'mp4',
            'profile': 'current',
            'src': [data['url']]
        }

        return info

site = NeteaseVideo()
