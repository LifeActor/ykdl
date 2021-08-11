#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.extractor import VideoExtractor
from ykdl.util.match import match1
from ykdl.util.html import get_content, get_location
from ykdl.videoinfo import VideoInfo


class Embed(VideoExtractor):
    name = "新浪视频 (sina)"

    def prepare(self):
        info = VideoInfo(self.name)

        vid = match1(self.url, '/(\d+)\.mp4')
        if vid:
            r_url = get_location('https://ask.ivideo.sina.com.cn/v_play_ipad.php?vid=' + vid)
        elif 'vid=' in self.url:
            r_url = get_location(self.url)

        info.stream_types.append('current')
        info.streams['current'] = {
            'container': 'mp4',
            'video_profile': 'current',
            'src': [r_url],
            'size' : 0
        }
        return info

site = Embed()
