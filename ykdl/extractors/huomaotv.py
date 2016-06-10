#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.html import get_content
from ..util.match import match1
from ..extractor import VideoExtractor
from ykdl.compact import urlencode, compact_bytes

import json

class HuomaoTv(VideoExtractor):
    name = u'火猫 (Huomao)'

    supported_stream_types = ['BD', 'TD', 'HD', 'SD' ]

    stream_2_profile = {'BD': u"原画", 'TD': u'超清', 'HD': u'高清', 'SD': u'标清' }

    live_base = "http://www.huomaotv.cn/swf/live_data"

    def prepare(self):
        self.live = True
        html = get_content(self.url)
        self.title = match1(html, '<title>([^<]+)').split('/')[0]

        video_name = match1(html, 'video_name = \'([^\']+)')
        params = { 'streamtype':'live',
                   'VideoIDS': video_name,
                   'cdns' : '1'
                }
        form = urlencode(params)
        content = get_content(self.live_base,data=compact_bytes(form, 'utf-8'),charset = 'utf-8')
        stream_data = json.loads(content)
        assert stream_data["roomStatus"] == "1", "The live stream is not online! "
        for stream in stream_data["streamList"]:
            if stream['default'] == 1:
                defstream = stream['list']

        for stream in defstream:
            self.stream_types.append(stream['type'])
            self.streams[stream['type']] = {'container': 'flv', 'video_profile': self.stream_2_profile[stream['type']], 'src' : [stream['url']], 'size': float('inf')}

        self.stream_types = sorted(self.stream_types, key = self.supported_stream_types.index)

site = HuomaoTv()
