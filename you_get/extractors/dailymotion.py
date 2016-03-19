#!/usr/bin/env python

from ..common import *
from ..extractor import VideoExtractor


class Dailymotion(VideoExtractor):
    name = "Dailymotion"

    supported_stream_types = ['720', '480', '380', '240' ]

    def prepare(self, **kwargs):
        assert self.url
        html = get_content(self.url)
        info = json.loads(match1(html, r'qualities":({.+?}),"'))
        self.title = match1(html, r'"video_title"\s*:\s*"(.+?)",')

        for stream in self.supported_stream_types:
            if stream in info.keys():
                url = info[stream][0]["url"]
                _, ext, size = url_info(url)
                self.stream_types.append(stream)
                self.streams[stream] = {'container': ext, 'src': [url], 'size' : size}

    def download_by_vid(self, param, **kwargs):
        pass

site = Dailymotion()
download = site.download_by_url
download_playlist = playlist_not_supported('dailymotion')
