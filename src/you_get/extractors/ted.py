#!/usr/bin/env python

from ..common import *
from ..extractor import VideoExtractor
import json

class Ted(VideoExtractor):
    name = "Ted"

    supported_stream_types = ['high', 'medium', 'low']

    def prepare(self, **kwargs):
        assert self.url
        html = get_html(self.url)
        metadata = json.loads(match1(html, r'({"talks"(.*)})\)'))
        self.title = metadata['talks'][0]['title']
        nativeDownloads = metadata['talks'][0]['nativeDownloads']
        for quality in self.supported_stream_types:
            if quality in nativeDownloads:
                url = nativeDownloads[quality]
                _, ext, size = url_info(url)
                self.streams[quality] = {'container': ext, 'video_profile': quality, 'src': [url], 'size' : size}
                self.stream_types.append(quality)

    def download_by_vid(self):
        pass

site = Ted()
download = site.download_by_url
download_playlist = playlist_not_supported('ted')
