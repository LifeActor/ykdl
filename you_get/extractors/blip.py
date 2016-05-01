#!/usr/bin/env python

from ..util.html import get_content, url_info
from ..extractor import VideoExtractor
import json

class Blip(VideoExtractor):
    name = "Blip"

    def prepare(self):
        assert self.url
        p_url = self.url + "?skin=json&version=2&no_wrap=1"
        html = get_content(p_url)
        metadata = json.loads(html)

        self.title = metadata['Post']['title']
        real_url = metadata['Post']['media']['url']
        _, ext, size = url_info(real_url)
        self.stream_types.append('current')
        self.streams['current'] = {'container': ext, 'src': [url], 'size' : size}

site = Blip()
