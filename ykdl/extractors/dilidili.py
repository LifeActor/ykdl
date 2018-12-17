#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.common import url_to_module

class Dilidili(VideoExtractor):
    name = u'嘀哩嘀哩（dilidili）'

    def prepare(self):
        info = VideoInfo(self.name)
        
        html = get_content(self.url)
        info.title = match1(html, r'<meta name="description" content="(.+?)" />')
        source_url = match1(html, r'var sourceUrl\s?=\s?"(.+?)"')
        ext = source_url.split('?')[0].split('.')[-1]
        
        # Dilidili hosts this video itself
        if ext in ('mp4', 'flv', 'f4v', 'm3u', 'm3u8'):
            t = 'default'
            info.stream_types.append(t)
            info.streams[t] = {
                'container': ext,
                'video_profile': t,
                'src': [source_url],
                'size' : 0
            }
            return info
        
        # It is an embedded video from other websites
        else:
            site, new_url = url_to_module(source_url)
            info_embedded = site.parser(new_url)
            info_embedded.title = info.title
            return info_embedded

site = Dilidili()
