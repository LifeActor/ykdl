#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.html import *
from ..util.match import *
from ..extractor import VideoExtractor

import json

class Miaopai(VideoExtractor):

    name = u'秒拍 (Miaopai)'

    def prepare(self):

        if not self.vid:
            self.vid = match1(self.url, 'http://www.miaopai.com/show/channel/([^.]+)', \
                                        'http://www.miaopai.com/show/([^.]+)', \
                                        'http://m.miaopai.com/show/channel/([^.]+)')
        content = json.loads(get_content('http://api.miaopai.com/m/v2_channel.json?fillType=259&scid={}&vend=miaopai'.format(self.vid)))

        assert content['status'] == 200, "something error!"

        content = content['result']
        self.title = content['ext']['t']
        url = content['stream']['base']
        ext = content['stream']['and']

        self.stream_types.append('current')
        self.streams['current'] = {'container': ext, 'src': [url], 'size' : 0}

    def prepare_list(self):
        html = get_content(self.url)
        video_list = match1(html, 'video_list=\[([^\]]+)')
        return matchall(video_list, ['\"([^\",]+)'])

site = Miaopai()
