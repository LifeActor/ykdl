#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from ..util.match import match1
from ..util.html import get_content, url_info
from ..extractor import VideoExtractor


class Dailymotion(VideoExtractor):
    name = "Dailymotion"

    supported_stream_types = ['720', '480', '380', '240' ]

    def prepare(self):
        html = get_content(self.url)
        info = json.loads(match1(html, r'qualities":({.+?}),"'))
        self.title = match1(html, r'"video_title"\s*:\s*"(.+?)",')

        for stream in self.supported_stream_types:
            if stream in info.keys():
                url = info[stream][0]["url"]
                _, ext, size = url_info(url)
                self.stream_types.append(stream)
                self.streams[stream] = {'container': ext, 'src': [url], 'size' : size}

site = Dailymotion()
