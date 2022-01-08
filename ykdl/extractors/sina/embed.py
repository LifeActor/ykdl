# -*- coding: utf-8 -*-

from .._common import *


class Embed(Extractor):
    name = '新浪视频 (sina)'

    def prepare(self):
        info = MediaInfo(self.name)

        vid = match1(self.url, '/(\d+)\.mp4')
        if vid:
            r_url = get_location(
                        'https://ask.ivideo.sina.com.cn/v_play_ipad.php',
                        params={'vid': vid})
        elif 'vid=' in self.url:
            r_url = get_location(self.url)

        info.streams['current'] = {
            'container': 'mp4',
            'video_profile': 'current',
            'src': [r_url],
            'size' : 0
        }
        return info

site = Embed()
