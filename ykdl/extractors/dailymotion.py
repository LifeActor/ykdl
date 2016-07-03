#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from ykdl.util.match import match1
from ykdl.util.html import get_content, url_info
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo


class Dailymotion(VideoExtractor):
    name = "Dailymotion"

    supported_stream_types = ['720', '480', '380', '240' ]

    def prepare(self):
        info = VideoInfo(self.name)
        html = get_content(self.url)
        data = json.loads(match1(html, r'qualities":({.+?}),"'))
        self.title = match1(html, r'"video_title"\s*:\s*"(.+?)",')

        for stream in self.supported_stream_types:
            if stream in info.keys():
                url = data[stream][0]["url"]
                _, ext, size = url_info(url)
                info.stream_types.append(stream)
                info.streams[stream] = {'container': ext, 'src': [url], 'size' : size}
        return info

site = Dailymotion()
