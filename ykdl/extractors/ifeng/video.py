# -*- coding: utf-8 -*-

from .._common import *


class IfengVideo(Extractor):
    name = '凤凰视频 (ifeng video)'  # Expired

    def prepare(self):
        return self.url[-13: -6]

    def prepare(self):
        info = MediaInfo(self.name)

        info.title = self.name + '-' + self.mid
        data = get_response(
                'http://tv.ifeng.com/html5/{self.mid}/video.json'
                .format(**vars())).json()
        if 'bqSrc' in data:
            info.streams['SD'] = {
                'container': 'mp4',
                'profile': '标清',
                'src': [data['bqSrc']]
            }
        if 'gqSrc' in data:
            info.streams['HD'] = {
                'container': 'mp4',
                'profile': '高清',
                'src': [data['gqSrc']]
            }
        return info

site = IfengVideo()
