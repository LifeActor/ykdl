# -*- coding: utf-8 -*-

from .._common import *


class BiliVC(Extractor):
    name = '哔哩哔哩 小视频 (Bili VC)'

    def prepare(self):
        return match1(self.url, 'video/(\d+)')

    def prepare(self):
        info = MediaInfo(self.name)

        video_data = get_response(
                'https://api.vc.bilibili.com/clip/v1/video/detail',
                params={'video_id': self.mid}).json()

        info.title = video_data['data']['item']['description']
        info.artist = video_data['data']['user']['name']

        info.streams['current'] = {
            'container': 'mp4',
            'profile': 'current',
            'src' : [video_data['data']['item']['video_playurl']],
            'size': int(video_data['data']['item']['video_size'])
        }

        return info

site = BiliVC()

