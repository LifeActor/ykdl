#!/usr/bin/env python

from ..common import *
from ..extractor import VideoExtractor

class Iqilu(VideoExtractor):
    name = "齐鲁网 (iqilu)"

    stream_types = [
        {'id': 'current', 'container': 'unknown', 'video_profile': 'currently'},
    ]

    def prepare(self, **kwargs):
        assert self.url
        assert re.match(r'http://v.iqilu.com/\w+', self.url)

        html = get_html(self.url)
        self.title = match1(html, r'<meta name="description" content="(.*?)\"\W')
        url = match1(html, r"<input type='hidden' id='playerId' url='(.+)'")

        container, ext, size = url_info(url)

        self.streams['current'] = {'container': ext, 'src': [url], 'size' : size}

    def download_by_vid(self, **kwargs):
        pass

site = Iqilu()
download = site.download_by_url
download_playlist = playlist_not_supported('iqilu')
