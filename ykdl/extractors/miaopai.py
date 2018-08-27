#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1, matchall
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo

import json

class Miaopai(VideoExtractor):

    name = u'秒拍 (Miaopai)'

    def prepare(self):
        info = VideoInfo(self.name)
        if not self.vid:
            self.vid = match1(self.url, 'https?://www.miaopai.com/show/channel/([^.]+)', \
                                        'https?://www.miaopai.com/show/([^.]+)', \
                                        'https?://m.miaopai.com/show/channel/([^.]+)')
        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, 'scid ?= ?[\'"]([^\'"]+)[\'"]')
        data = json.loads(get_content('http://api.miaopai.com/m/v2_channel.json?fillType=259&scid={}&vend=miaopai'.format(self.vid)))

        assert data['status'] == 200, "something error!"

        data = data['result']
        info.title = data['ext']['t'] or self.name + '_' + self.vid
        url = data['stream']['base']
        ext = data['stream']['and']

        info.stream_types.append('current')
        info.streams['current'] = {'container': ext, 'src': [url], 'size' : 0}
        return info

    def prepare_list(self):
        html = get_content(self.url)
        video_list = match1(html, 'video_list=\[([^\]]+)')
        return matchall(video_list, ['\"([^\",]+)'])

site = Miaopai()
