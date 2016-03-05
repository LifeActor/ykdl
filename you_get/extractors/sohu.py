#!/usr/bin/env python
from ..common import playlist_not_supported
from ..embedextractor import EmbedExtractor

import re

class Sohu(EmbedExtractor):

    def prepare(self, **kwargs):
        assert self.url

        if re.search('my.tv.sohu.com', self.url):
            self.video_url.append(('mysohu',self.url))
        else:
            self.video_url.append(('tvsohu',self.url))


site = Sohu()
download = site.download_by_url
download_playlist = playlist_not_supported('sohu')
