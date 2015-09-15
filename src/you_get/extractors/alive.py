#!/usr/bin/env python

from ..common import *
from ..extractor import VideoExtractor

class Alive(VideoExtractor):
    name = "Alive"

    stream_types = [
        {'id': 'current', 'container': 'unknown', 'video_profile': 'currently'},
    ]

    def prepare(self, **kwargs):
        assert self.url
        html = get_html(self.url)
        self.title = r1(r'<meta property="og:title" content="([^"]+)"', html)
        url = r1(r'file: "(http://alive[^"]+)"', html)
        print(self.title, url)
        container, ext, size = url_info(url)

        self.streams['current'] = {'container': ext, 'src': [url], 'size' : size}

site = Alive()
download = site.download_by_url
download_playlist = playlist_not_supported('Alive')
