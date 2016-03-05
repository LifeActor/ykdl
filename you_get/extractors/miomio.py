#!/usr/bin/env python

from ..common import *
from ..embedextractor import EmbedExtractor

class Miomio(EmbedExtractor):

    def prepare(self, **kwargs):
        assert self.url
        html = get_content(self.url)
        self.title = r1(r'<meta name="description" content="([^"]*)"', html)
        flashvars = r1(r'flashvars="(type=[^"]*)"', html)
        t = r1(r'type=(\w+)', flashvars)
        id = r1(r'vid=([^&]+)', flashvars)
        print(t,id)
        if t == 'video':
            t = 'sina'

        self.video_info.append((t, id))

site = Miomio()
download = site.download_by_url
download_playlist = playlist_not_supported('miomio')
