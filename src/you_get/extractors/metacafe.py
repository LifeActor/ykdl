#!/usr/bin/env python

from ..common import *
import urllib.error
from urllib.parse import unquote
from ..extractor import VideoExtractor

class Metacafe(VideoExtractor):
    name = "Metacafe"

    stream_types = [
        {'id': 'current', 'container': 'unknown', 'video_profile': 'currently'},
    ]

    def prepare(self, **kwargs):
        assert self.url and re.match(r'http://www.metacafe.com/watch/\w+', self.url)

        html = get_html(self.url, faker = True)
        self.title = r1(r'<meta property="og:title" content="([^"]*)"', html)
        url_raw = match1(html, '&videoURL=([^&]+)')
        print(url_raw)
        
        url = unquote(url_raw)

        container, ext, size = url_info(url)

        self.streams['current'] = {'container': ext, 'src': [url], 'size' : size}

    def download_by_vid(self, **kwargs):
        pass

site = Metacafe()
download = site.download_by_url
download_playlist = playlist_not_supported('metacafe')
