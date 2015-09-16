#!/usr/bin/env python

from ..common import *
from ..extractor import VideoExtractor

class JPopsuki(VideoExtractor):
    name = "JPopsuki"

    stream_types = [
        {'id': 'current', 'container': 'unknown', 'video_profile': 'currently'},
    ]

    def prepare(self, **kwargs):
        assert self.url
        html = get_html(self.url, faker = True)
        self.title =  r1(r'<meta name="title" content="([^"]*)"', html)
        url = "http://jpopsuki.tv%s" % r1(r'<source src="([^"]*)"', html)

        container, ext, size = url_info(url)

        self.streams['current'] = {'container': ext, 'src': [url], 'size' : size}

    def download_by_vid(self, **kwargs):
        pass

site = JPopsuki()
download = site.download_by_url
download_playlist = playlist_not_supported('jpopsuki')
