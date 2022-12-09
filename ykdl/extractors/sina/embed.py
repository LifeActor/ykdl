# -*- coding: utf-8 -*-

from .._common import *


class Embed(Extractor):
    name = '新浪视频 (sina)'

    def prepare(self):
        info = MediaInfo(self.name)

        vid = match1(self.url, '/(\d+)\.mp4', 'vid=(\d+)')
        url = 'https://ask.ivideo.sina.com.cn/v_play_ipad.php?' + urlencode({'vid': vid})

        info.streams['current'] = {
            'container': 'mp4',
            'profile': 'current',
            'src': [url]
        }
        return info

site = Embed()
