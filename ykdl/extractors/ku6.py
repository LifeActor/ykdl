#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content, url_info
from ykdl.util.match import match1
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo

import json
import re

class Ku6(VideoExtractor):
    name = u"酷6 (Ku6)"

    def prepare(self):
        info = VideoInfo(self.name)
        if self.url and not self.vid:
            self.vid = match1(self.url, 'http://v.ku6.com/special/show_\d+/(.*)\.html',
            'http://v.ku6.com/show/(.*)\.html',
            'http://my.ku6.com/watch\?.*v=(.*).*')

        video_data = json.loads(get_content('http://v.ku6.com/fetchVideo4Player/%s.html' % self.vid))
        data = video_data['data']
        assert video_data['status'] == 1, '%s : %s' % (self.name, data)
        info.title = data['t']
        f = data['f']


        urls = f.split(',')
        ext = re.sub(r'.*\.', '', urls[0])
        assert ext in ('flv', 'mp4', 'f4v'), ext
        ext = {'f4v': 'flv'}.get(ext, ext)
        size = 0
        for url in urls:
            _, _, temp = url_info(url)
            size += temp

        info.streams['current'] = {'container': ext, 'src': urls, 'size' : size}
        info.stream_types.append('current')
        return info

site = Ku6()
