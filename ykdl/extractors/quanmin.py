#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.util.html import get_content
from ykdl.util.match import match1
import json

class Panda(VideoExtractor):
    name = u'全民直播 (QuanminLive)'

    api_url = "http://www.quanmin.tv/json/rooms/{}/info4.json"
    live_base = "http://flv.quanmin.tv/live/{}.flv"

    def prepare(self):
        info = VideoInfo(self.name, True)
        if not self.vid:
            self.vid = match1(self.url, 'quanmin.tv/(\w+)')

        content = get_content(self.api_url.format(self.vid))
        stream_data = json.loads(content)
        assert stream_data['status'], u"error: (⊙o⊙)主播暂时不在家，看看其他精彩直播吧！"
        info.title = stream_data["title"]
        info.artist = stream_data['nick']


        info.stream_types.append('current')
        info.streams['current'] = {'container': 'flv', 'video_profile': 'current', 'src' : [self.live_base.format(self.vid)], 'size': float('inf')}
        return info

site = Panda()
