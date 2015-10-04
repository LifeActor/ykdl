#!/usr/bin/env python

from ..common import *
from ..extractor import VideoExtractor


class Instagram(VideoExtractor):
    name = "Instagram"

    def prepare(self, **kwargs):
        assert self.url or self.vid

        if not self.url:
            self.url = 'instagram.com/p/{}'.format(self.vid)

        if not self.vid:
            self.vid = match1(self.url, 'instagram.com/p/([^/]+)')

        html = get_content(self.url)
        self.title = match1(html, '<meta property="og:title" content="([^"]*)"')
        stream = match1(html, '<meta property="og:video" content="([^"]*)"')
        mime, ext, size = url_info(stream)
        self.streams['current'] = {'container': ext, 'src': [stream], 'size' : size}
        self.stream_types.append('current')


site = Instagram()
download = site.download_by_url
download_playlist = playlist_not_supported('instagram')
