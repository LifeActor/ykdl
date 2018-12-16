#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo

import json

class DownloadDirectly(VideoExtractor):
    name = u'Download directly'

    def prepare(self):
        info = VideoInfo(self.name)
        info.title = self.url.split('?')[0].split('/')[-1]
        info.stream_types = 'default'
        info.streams['default'] = {
            'container': self.url.split('?')[0].split('.')[-1],
            'video_profile': 'default',
            'src': [self.url],
            'size': 0
        }
        return info

site = DownloadDirectly()
