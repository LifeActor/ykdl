#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
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
        if self.url:
            self.vid = match1(self.url, 'show/(.*)')

        json_request_url = "https://v.douyu.com/api/swf/getvideourl/{}".format(self.vid)
        tt = int(time.time())
        did = uuid.uuid4().hex.upper()
        sign_content = '{room_id}{did}A12Svb&%1UUmf@hC{tt}'.format(room_id = self.vid, did = did, tt = tt)
        sign = hashlib.md5(sign_content.encode('utf-8')).hexdigest()
        params = {
            'sign': sign,
            'vid': self.vid,
            'did': did,
            'tt': tt
        }
        form = urlencode(params)

        video_data = json.loads(get_content(json_request_url, data=compact_bytes(form,'utf-8')))
        assert video_data['error'] == 0, video_data
        real_url = video_data['data']['thumb_video']['normal']['url']
        info.stream_types.append('current')
        info.streams['current'] = {'container': 'flv', 'video_profile': 'current', 'src' : [real_url], 'size': 0}
        info.title = video_data['data']['title']
        return info

site = DouyutvVideo()
