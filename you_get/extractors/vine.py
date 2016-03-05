#!/usr/bin/env python

from ..common import *
from ..extractor import VideoExtractor

class Vine(VideoExtractor):
    name = 'Vine'

    def prepare(self, **kwargs):
        assert self.url or self.vid

        if self.url and not self.vid:
            self.vid = match1(self.url, 'vine.co/v/([^/]+)')
        else:
            self.url = "https://vine.co/v/{}/".format(self.vid)

        html = get_content(self.url)

        title1 = match1(html, '<meta property="twitter:title" content="([^"]*)"')
        title2 = r1(html, '<meta property="twitter:description" content="([^"]*)"')
        self.title = "{} - {} [{}]".format(title1, title2, self.vid)

        stream = match1(html, '<meta property="twitter:player:stream" content="([^"]*)">')

        mime, ext, size = url_info(stream)

        self.stream_types.append('current')
        self.streams['current'] = {'container': ext, 'src': [stream], 'size': size }

site = Vine()
download = site.download_by_url
download_playlist = playlist_not_supported('vine')
