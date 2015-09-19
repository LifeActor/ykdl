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
            self.vid = r1(r'instagram.com/p/([^/]+)', self.url)

        html = get_html(self.url)
        description = r1(r'<meta property="og:title" content="([^"]*)"', html)
        self.title = "{} [{}]".format(description.strip(), vid)
        stream = r1(r'<meta property="og:video" content="([^"]*)"', html)
        mime, ext, size = url_info(stream)
        self.streams['current'] = {'container': ext, 'src': [stream], 'size' : size}
        self.stream_types.append('current')


site = Instagram()
download = site.download_by_url
download_playlist = playlist_not_supported('instagram')
