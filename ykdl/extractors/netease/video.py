# -*- coding: utf-8 -*-

from .._common import *


class NeteaseVideo(Extractor):
    name = '网易视频 (163)'

    def prepare(self):
        info = MediaInfo(self.name)

        if self.vid is None:
            self.vid = match1(self.url, '(\w+)\.html')

        data = get_response('https://so.v.163.com/v6/video/videodetail.do',
                            params={
                               'vid': self.vid,
                               'adapter': 1
                            }).json()
        assert data['code'] == 1, data['msg']

        data = data['data']
        info.title = data['title']
        info.artist = data.get('username')
        info.streams['current'] = {
            'container': 'mp4',
            'video_profile': 'current',
            'src' : [data['url']],
            'size': 0
        }
        return info

site = NeteaseVideo()
