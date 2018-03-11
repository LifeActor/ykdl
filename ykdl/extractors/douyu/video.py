#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content, add_header
from ykdl.util.match import match1, matchall
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.compact import urlencode,compact_bytes

import hashlib
import time
import json
import uuid

class DouyutvVideo(VideoExtractor):
    name = u'斗鱼视频 (DouyuTV)'

    def prepare(self):
        info = VideoInfo(self.name)
        add_header('X-Requested-With', 'XMLHttpRequest')
        if self.url:
            self.vid = match1(self.url, 'show/(.*)')

        json_request_url = "https://vmobile.douyu.com/video/getInfo?vid={}".format(self.vid)

        video_data = json.loads(get_content(json_request_url))
        assert video_data['error'] == 0, video_data
        real_url = video_data['data']['video_url']
        info.stream_types.append('current')
        info.streams['current'] = {'container': 'm3u8', 'video_profile': 'current', 'src' : [real_url], 'size': 0}
        info.title = self.name + '_' + self.vid
        return info

site = DouyutvVideo()
