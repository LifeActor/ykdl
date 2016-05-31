#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.html import get_content, url_info
from ..extractor import VideoExtractor
import json

class SoundCloud(VideoExtractor):
    name = "SoundCloud"

    def prepare(self):

        if self.url and not self.vid:
            metadata = get_content('https://api.soundcloud.com/resolve.json?url=' + self.url + '&client_id=02gUJC0hH2ct1EGOcYXQIzRFU91c72Ea')
            info = json.loads(metadata)
            self.title = info["title"]
            self.vid = str(info["id"])
        else:
            self.title = self.name + "-" + self.vid

        url = 'https://api.soundcloud.com/tracks/' + self.vid + '/stream?client_id=02gUJC0hH2ct1EGOcYXQIzRFU91c72Ea'

        type, ext, size = url_info(url)

        self.streams['current'] = {'container': ext, 'src': [url], 'size' : size}
        self.stream_types.append('current')
 
site = SoundCloud()
