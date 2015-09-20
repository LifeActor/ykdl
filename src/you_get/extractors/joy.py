#!/usr/bin/env python

from ..common import *
from ..extractor import VideoExtractor

class Joy(VideoExtractor):

    name = '激动网 (Joy)'


    def prepare(self, **kwargs):
        assert self.url or self.vid

        if not self.vid:
            self.vid = match1(self.url, 'resourceId=([0-9]+)')
        if not self.url:
            self.url = "http://www.joy.cn/video?resourceId={}".format(self.vid)

        html= get_html(self.url, faker = True)

        self.title = match1(html, '<meta content=\"([^\"]+)')

        url = match1(html, '<source src=\"([^\"]+) type="video/mp4"> 您的浏览器')

        _, ext, size = url_info(url)

        self.stream_types.append('current')
        self.streams['current'] = {'container': ext, 'src': [url], 'size': size }

site = Joy()
download = site.download_by_url
download_playlist = playlist_not_supported('joy')
