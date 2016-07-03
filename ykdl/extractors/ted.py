#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content, url_info
from ykdl.util.match import match1
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
import json

class Ted(VideoExtractor):
    name = "Ted"

    supported_stream_types = ['high', 'medium', 'low']
    types_2_id = {'high': 'HD', 'medium': 'SD', 'low': 'LD'}
    types_2_profile = {'high': u'高清', 'medium': u'标清', 'low': u'急速'}

    def prepare(self):
        info = VideoInfo(self.name)
        html = get_content(self.url)
        metadata = json.loads(match1(html, r'({"talks"(.*)})\)'))
        info.title = metadata['talks'][0]['title']
        nativeDownloads = metadata['talks'][0]['nativeDownloads']
        for quality in self.supported_stream_types:
            if quality in nativeDownloads:
                url = nativeDownloads[quality]
                _, ext, size = url_info(url)
                stream_id = self.types_2_id[quality]
                stream_profile = self.types_2_profile[quality]
                info.streams[stream_id] = {'container': ext, 'video_profile': stream_profile, 'src': [url], 'size' : size}
                info.stream_types.append(stream_id)
        return info

site = Ted()
