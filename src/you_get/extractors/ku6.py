#!/usr/bin/env python

from ..common import *

import json
from ..extractor import VideoExtractor

class Ku6(VideoExtractor):
    name = "酷6 (Ku6)"

    stream_types = [
        {'id': 'current', 'container': 'unknown', 'video_profile': 'currently'},
    ]

    def prepare(self, **kwargs):
        assert self.url or self.vid
        patterns = [r'http://v.ku6.com/special/show_\d+/(.*)\.\.\.html',
            r'http://v.ku6.com/show/(.*)\.\.\.html',
            r'http://my.ku6.com/watch\?.*v=(.*)\.\..*']
        if self.url and not self.vid:
            self.vid = r1_of(patterns, self.url)

        self.ku6_download_by_id()

    def ku6_download_by_id(self):
        data = json.loads(get_html('http://v.ku6.com/fetchVideo4Player/%s...html' % self.vid))['data']

        self.title = data['t']
        f = data['f']


        urls = f.split(',')
        ext = re.sub(r'.*\.', '', urls[0])
        assert ext in ('flv', 'mp4', 'f4v'), ext
        ext = {'f4v': 'flv'}.get(ext, ext)
        size = 0
        for url in urls:
            _, _, temp = url_info(url)
            size += temp

        self.streams['current'] = {'container': ext, 'src': urls, 'size' : size}

site = Ku6()
download = site.download_by_url
download_playlist = playlist_not_supported('ku6')
