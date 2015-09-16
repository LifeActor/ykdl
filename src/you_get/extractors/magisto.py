#!/usr/bin/env python

from ..common import *
from ..extractor import VideoExtractor

class Magisto(VideoExtractor):
    name = "Magisto"

    stream_types = [
        {'id': 'current', 'container': 'unknown', 'video_profile': 'currently'},
    ]

    def prepare(self, **kwargs):
        assert self.url
        html = get_html(self.url)
        title1 = r1(r'<meta name="twitter:title" content="([^"]*)"', html)
        title2 = r1(r'<meta name="twitter:description" content="([^"]*)"', html)
        video_hash = r1(r'http://www.magisto.com/video/([^/]+)', self.url)
        self.title = "%s %s - %s" % (title1, title2, video_hash)
        url = r1(r'<source type="[^"]+" src="([^"]*)"', html)

        container, ext, size = url_info(url)

        self.streams['current'] = {'container': ext, 'src': [url], 'size' : size}

    def download_by_vid(self, **kwargs):
        pass

site = Magisto()
download = site.download_by_url
download_playlist = playlist_not_supported('magisto')
