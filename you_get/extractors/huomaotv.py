#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.html import get_content
from ..util.match import match1
from ..extractor import VideoExtractor
import sys
import sys
if sys.version_info[0] == 3:
    from urllib.parse import urlencode
else:
    from urllib import urlencode
import json

class HuomaoTv(VideoExtractor):
    name = '火猫 (Huomao)'

    supported_stream_types = ['BD', 'TD', 'HD', 'SD' ]

    stream_2_profile = {'BD':"原画", 'TD': '超清', 'HD': '高清', 'SD': '标清' }

    live_base = "http://www.huomaotv.cn/swf/live_data"

    def prepare(self):

        html = get_content(self.url)
        self.title = match1(html, '<title>([^<]+)')

        video_name = match1(html, 'video_name = \'([^\']+)')
        params = { 'streamtype':'live',
                   'VideoIDS': video_name,
                   'cdns' : '1'
                }
        form = urlencode(params)
        content = get_content(self.live_base,data=bytes(form, 'utf-8'),charset = 'utf-8')
        stream_data = json.loads(content)
        if stream_data["roomStatus"] == "1":
            for stream in stream_data["streamList"]:
                if stream['default'] == 1:
                    defstream = stream['list']
        else:
           from ..util import log
           log.e("The live stream is not online! ")
           exit(1)
        for stream in defstream:
            self.stream_types.append(stream['type'])
            self.streams[stream['type']] = {'container': 'flv', 'video_profile': self.stream_2_profile[stream['type']], 'src' : [stream['url']], 'size': float('inf')}

        self.stream_types = sorted(self.stream_types, key = self.supported_stream_types.index)

site = HuomaoTv()
