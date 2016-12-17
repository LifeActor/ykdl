#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.util.html import get_content
from ykdl.util.match import match1, matchall


class BiliLive(VideoExtractor):
    name = u"Bilibili live (哔哩哔哩 直播)"

    def prepare(self):
        info = VideoInfo(self.name, True)
        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, 'var ROOMID = (\d+);')
            t = match1(html, '<title>([^<]+)').split('-')
            info.title = t[0]
            info.artist = t[1]

        data = get_content('http://live.bilibili.com/api/playurl?cid={}'.format(self.vid))
        urls = [matchall(data, ['CDATA\[([^\]]+)'])[1]]
        size = float('inf')
        ext = 'flv'

        info.stream_types.append('current')
        info.streams['current'] = {'container': ext, 'video_profile': 'current', 'src' : urls, 'size': size}
        return info

site = BiliLive()
