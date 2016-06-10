#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.extractor import VideoExtractor
from ykdl.util.html import get_content
from ykdl.util.match import match1, matchall


class BiliLive(VideoExtractor):
    name = u"Bilibili live (哔哩哔哩 直播)"

    def prepare(self):
        self.live = True
        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, 'cid=([^&]+)')
            t = match1(html, '<title>([^<]+)').split('-')
            self.title = t[0]
            self.artist = t[1]

        info = get_content('http://live.bilibili.com/api/playurl?cid={}'.format(self.vid))
        urls = [matchall(info, ['CDATA\[([^\]]+)'])[1]]
        size = float('inf')
        ext = 'flv'

        self.stream_types.append('current')
        self.streams['current'] = {'container': ext, 'video_profile': 'current', 'src' : urls, 'size': size}




site = BiliLive()
