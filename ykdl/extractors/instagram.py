#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.match import match1
from ykdl.util.html import get_content, url_info
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo


class Instagram(VideoExtractor):
    name = "Instagram"

    def prepare(self):
        info = VideoInfo(self.name)
        if not self.url:
            self.url = 'instagram.com/p/{}'.format(self.vid)

        if not self.vid:
            self.vid = match1(self.url, 'instagram.com/p/([^/]+)')

        html = get_content(self.url)
        info.title = match1(html, '<meta property="og:title" content="([^"]*)"')
        stream = match1(html, '<meta property="og:video" content="([^"]*)"')
        mime, ext, size = url_info(stream)
        info.streams['current'] = {'container': ext, 'src': [stream], 'size' : size}
        info.stream_types.append('current')


site = Instagram()
