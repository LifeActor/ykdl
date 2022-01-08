# -*- coding: utf-8 -*-

from .._common import *


class IfengVideo(Extractor):
    name = '凤凰视频 (ifeng video)'  # Expired

    def prepare(self):
        info = MediaInfo(self.name)
        self.vid = self.url[-13: -6]
        info.title = self.name + '-' + self.vid
        data = get_response(
                'http://tv.ifeng.com/html5/{self.vid}/video.json'
                .format(**vars())).json()
        if 'bqSrc' in data:
            info.streams['SD'] = {
                'container': 'mp4',
                'video_profile': '标清',
                'src' : [data['bqSrc']],
                'size': 0
            }
        if 'gqSrc' in data:
            info.streams['HD'] = {
                'container': 'mp4',
                'video_profile': '高清',
                'src' : [data['gqSrc']],
                'size': 0
            }
        return info

site = IfengVideo()
