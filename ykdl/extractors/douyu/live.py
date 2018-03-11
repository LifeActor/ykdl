#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1, matchall
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.compact import urlencode,compact_bytes

import time
import hashlib
import random
import json
import sys

APPKEY = 'zNzMV1y4EMxOHS6I5WKm' #from android-hd client


douyu_match_pattern = [ 'class="hroom_id" value="([^"]+)',
                        'data-room_id="([^"]+)'
                      ]
class Douyutv(VideoExtractor):
    name = u'斗鱼直播 (DouyuTV)'

    stream_ids = ['TD', 'HD', 'SD']
    stream_id_2_rate = {'TD':3 , 'HD':2, 'SD':1}
    id_2_profile = {'TD': u'超清' , 'HD':u'高清', 'SD':u'标清'}

    def prepare(self):
        info = VideoInfo(self.name, True)

        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, '"room_id.?":(\d+)') or match1(html, 'data-onlineid=(\d+)')
        cdn = 'ws'
        authstr = 'room/{0}?aid=wp&cdn={1}&client_sys=wp&time={2}'.format(self.vid, cdn, int(time.time()))
        authmd5 = hashlib.md5((authstr + APPKEY).encode()).hexdigest()
        api_url = 'https://capi.douyucdn.cn/api/v1/{0}&auth={1}'.format(authstr,authmd5)
        html_content = get_content(api_url)
        live_data = json.loads(html_content)

        assert live_data["error"] == 0, "server error!!"
        live_data = live_data["data"]
        assert live_data['show_status'] == '1', "the show is not online!!"
        info.title = live_data['room_name']
        info.artist = live_data['nickname']
        real_url = '/'.join([live_data['rtmp_url'], live_data['rtmp_live']])
        info.stream_types.append('TD')
        info.streams['TD'] = {'container': 'flv', 'video_profile': self.id_2_profile['TD'], 'src' : [real_url], 'size': float('inf')}

        return info

    def prepare_list(self):

        html = get_content(self.url)
        return matchall(html, douyu_match_pattern)

site = Douyutv()
