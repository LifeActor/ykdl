#!/usr/bin/env python

from ..common import *
from ..extractor import VideoExtractor

class Vid48(VideoExtractor):
    name = 'Vid48'

    def prepare(self, **kwargs):
        assert self.url or self.vid

        if self.url and not self.vid:
            self.vid = match1(self.url, 'v=([^&]*)')

        p_url = "http://vid48.com/embed_player.php?vid=%s&autoplay=yes" % self.vid

        html = get_html(p_url)
    
        self.title = match1( html, '<title>(.*)</title>')
        url = "http://vid48.com%s" % match1(html, 'file: "([^"]*)"')
        _, ext, size = url_info(url)

        self.streams['current'] = {'container': ext, 'src': [url], 'size': size }
        self.stream_types.append('current')



site = Vid48()
download = site.download_by_url
download_playlist = playlist_not_supported('vid48')
