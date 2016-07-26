#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.compact import urlencode, compact_bytes

import json

class HuomaoTv(VideoExtractor):
    name = u'火猫 (Huomao)'

    supported_stream_types = ['BD', 'TD', 'HD', 'SD' ]

    stream_2_profile = {'BD': u"原画", 'TD': u'超清', 'HD': u'高清', 'SD': u'标清' }

    live_base = "http://www.huomao.com/swf/live_data"

    def prepare(self):
        info = VideoInfo(self.name, True)
        html = get_content(self.url)
        info.title = match1(html, '<title>([^<]+)').split('_')[0]

        video_name = match1(html, 'getFlash\("[0-9]+","([^"]+)')
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
            info.stream_types.append(stream['type'])
            info.streams[stream['type']] = {'container': 'flv', 'video_profile': self.stream_2_profile[stream['type']], 'src' : [stream['url']], 'size': float('inf')}

        info.stream_types = sorted(info.stream_types, key = self.supported_stream_types.index)
        return info

site = HuomaoTv()
