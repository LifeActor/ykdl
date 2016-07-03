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
            self.vid = self.url[self.url.rfind('/')+1:]

        suffix = 'room/%s?aid=android&client_sys=android&time=%d' % (self.vid, int(time.time()))
        sign = hashlib.md5((suffix + '1231').encode('ascii')).hexdigest()
        json_request_url = "http://www.douyutv.com/api/v1/%s&auth=%s" % (suffix, sign)
        content = get_content(json_request_url)
        data = json.loads(content)['data']
        server_status = data.get('error',0)
        if server_status is not 0:
            raise ValueError("Server returned error:%s" % server_status)
        info.title = data.get('room_name')
        info.artist= data.get('nickname')
        show_status = data.get('show_status')
        assert show_status == "1", "The live stream is not online! (Errno:%s)" % show_status
        real_url = data.get('rtmp_url')+'/'+data.get('rtmp_live')
        info.stream_types.append('current')
        info.streams['current'] = {'container': 'flv', 'video_profile': 'current', 'src' : [real_url], 'size': float('inf')}
        return info

    def prepare_list(self):

        html = get_content(self.url)
        return matchall(html, douyu_match_pattern)

site = Douyutv()
