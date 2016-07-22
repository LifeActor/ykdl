#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1, matchall
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo

import hashlib
import time
import json

douyu_match_pattern = [ 'class="hroom_id" value="([^"]+)',
                        'data-room_id="([^"]+)'
                      ]
class Douyutv(VideoExtractor):
    name = u'斗鱼 (DouyuTV)'

    def prepare(self):
        info = VideoInfo(self.name, True)
        if self.url:
            self.vid = match1(self.url, '/(\d+)')

        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, '"room_id":(\d+)')

        json_request_url = "http://m.douyu.com/html5/live?roomId={}".format(self.vid)
        content = json.loads(get_content(json_request_url))
        assert content['error'] == 0, '%s: %s' % (self.name, content['msg'])
        data = content['data']
        info.title = data.get('room_name')
        info.artist= data.get('nickname')
        show_status = data.get('show_status')
        assert show_status == "1", "The live stream is not online! (Errno:%s)" % show_status
        real_url = data.get('hls_url')
        info.stream_types.append('current')
        info.streams['current'] = {'container': 'm3u8', 'video_profile': 'current', 'src' : [real_url], 'size': float('inf')}
        return info

    def prepare_list(self):

        html = get_content(self.url)
        return matchall(html, douyu_match_pattern)

site = Douyutv()
