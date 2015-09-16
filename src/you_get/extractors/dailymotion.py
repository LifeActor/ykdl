#!/usr/bin/env python

from ..common import *
from ..extractor import VideoExtractor


class Dailymotion(VideoExtractor):
    name = "Dailymotion"

    stream_types = [
        {'id': '720', 'container': 'unknown', 'video_profile': '720p'},
        {'id': '480', 'container': 'unknown', 'video_profile': '480p'},
        {'id': '380', 'container': 'unknown', 'video_profile': '380p'},
        {'id': '240', 'container': 'unknown', 'video_profile': '240p'},
    ]

    def prepare(self, **kwargs):
        assert self.url
        html = get_content(self.url)
        info = json.loads(match1(html, r'qualities":({.+?}),"'))
        self.title = match1(html, r'"video_title"\s*:\s*"(.+?)",')

        for stream in self.stream_types:
            if stream['id'] in info.keys():
                url = info[stream['id']][0]["url"]
                _, ext, size = url_info(url)
                self.streams[stream['id']] = {'container': ext, 'src': [url], 'size' : size}

    def download_by_vid(self, **kwargs):
        pass

site = Dailymotion()
download = site.download_by_url
download_playlist = playlist_not_supported('dailymotion')
