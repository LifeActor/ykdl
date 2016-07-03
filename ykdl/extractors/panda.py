#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.util.html import get_content
from ykdl.util.match import match1
import json

class Panda(VideoExtractor):
    name = u'熊猫TV (Panda)'

    live_base = "http://pl3.live.panda.tv/live_panda/{}.flv"
    api_url = "http://www.panda.tv/api_room?roomid={}"

    def prepare(self):
        info = VideoInfo(self.name, True)
        if not self.vid:
            self.vid = match1(self.url, 'panda.tv/(\w+)')

        content = get_content(self.api_url.format(self.vid))
        stream_data = json.loads(content)
        assert stream_data['data']['videoinfo']['status'] == '2', u"error: (⊙o⊙)主播暂时不在家，看看其他精彩直播吧！"
        room_key = stream_data['data']['videoinfo']['room_key']
        info.title = stream_data['data']['roominfo']['name']
        info.artist = stream_data['data']['hostinfo']['name']


        info.stream_types.append('current')
        info.streams['current'] = {'container': 'flv', 'video_profile': 'current', 'src' : [self.live_base.format(room_key)], 'size': float('inf')}
        return info

site = Panda()
