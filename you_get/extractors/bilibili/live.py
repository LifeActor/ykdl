#!/usr/bin/env python

from you_get.extractor import VideoExtractor
from you_get.util.html import get_content
from you_get.util.match import match1, matchall


class BiliLive(VideoExtractor):
    name = "Bilibili live (哔哩哔哩 直播)"
    def prepare(self):

        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, 'cid=([^&]+)')
            self.title = match1(html, '<title>([^<]+)')

        else:
            if not self.title:
                self.title = self.name + "-" + self.vid

        info = get_content('http://live.bilibili.com/api/playurl?cid={}'.format(self.vid))
        urls = [matchall(info, ['CDATA\[([^\]]+)'])[1]]
        size = float('inf')
        ext = 'flv'

        self.stream_types.append('current')
        self.streams['current'] = {'container': ext, 'video_profile': 'current', 'src' : urls, 'size': size}




site = BiliLive()
