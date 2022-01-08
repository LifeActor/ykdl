# -*- coding: utf-8 -*-

from .._common import *


class HuajiaoVideo(Extractor):
    name = 'huajiao video (花椒小视频)'

    def prepare(self):
        info = MediaInfo(self.name, True)

        self.vid = match1(self.url, 'vid=(\d+)')

        html = get_content(self.url)
        video_data = json.loads(match1(html, '_DATA.list = (\[[^\[]+?]);'))

        if self.vid:
            for data in video_data:
                if data['vid']  == self.vid:
                    break
        else:
            data = video_data[0]
        assert 'video_url' in data, 'No video found!!'

        info.artist = data['user_name']
        info.title = data['video_name']
        info.streams['current'] = {
            'container': 'mp4',
            'src': [data['video_url']],
            'size' : 0
        }
        return info

site = HuajiaoVideo()
