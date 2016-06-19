#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content, url_info
from ykdl.util.match import match1
from ykdl.extractor import VideoExtractor
import json

class Ted(VideoExtractor):
    name = "Ted"

    supported_stream_types = ['high', 'medium', 'low']

    def prepare(self):
        html = get_content(self.url)
        metadata = json.loads(match1(html, r'({"talks"(.*)})\)'))
        self.title = metadata['talks'][0]['title']
        nativeDownloads = metadata['talks'][0]['nativeDownloads']
        for quality in self.supported_stream_types:
            if quality in nativeDownloads:
                url = nativeDownloads[quality]
                _, ext, size = url_info(url)
                self.streams[quality] = {'container': ext, 'video_profile': quality, 'src': [url], 'size' : size}
                self.stream_types.append(quality)

site = Ted()
