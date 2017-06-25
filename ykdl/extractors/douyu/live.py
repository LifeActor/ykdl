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

from .get_douyulive_url_blackbox import stupidMD5

API_KEY = 'a2053899224e8a92974c729dceed1cc99b3d8282'
VER = '2017061511'



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
            room = match1(html, 'var $ROOM = ([^;]+)')
            self.vid = match1(html, '"room_id.?":(\d+)')
            info.title = json.loads("{\"room_name\" : \"" + match1(html, '"room_name.?":"([^"]+)') + "\"}")['room_name']
            info.artist = json.loads("{\"name\" : \"" + match1(html, '"owner_name.?":"([^"]+)') + "\"}")['name']
        api_url = 'https://www.douyu.com/lapi/live/getPlay/{}'.format(self.vid)
        tt = str(int(time.time() / 60))
        rnd_md5 = hashlib.md5(str(random.random()).encode('utf8'))
        did = rnd_md5.hexdigest().upper()
        to_sign = ''.join([self.vid, did, API_KEY, tt])
        sign = stupidMD5(to_sign)
        for stream in self.stream_ids:
            rate = self.stream_id_2_rate[stream]
            params = {"ver" : VER, "sign" : sign, "did" : did, "rate" : rate, "tt" : tt, "cdn" : "ws"}
            form = urlencode(params)
            html_content = get_content(api_url, data=compact_bytes(form, 'utf-8'))
            live_data = json.loads(html_content)
            assert live_data["error"] == 0, "live show is offline"
            live_data = live_data["data"]
            real_url = '/'.join([live_data['rtmp_url'], live_data['rtmp_live']])

            info.stream_types.append(stream)
            info.streams[stream] = {'container': 'flv', 'video_profile': self.id_2_profile[stream], 'src' : [real_url], 'size': float('inf')}

        return info

    def prepare_list(self):

        html = get_content(self.url)
        return matchall(html, douyu_match_pattern)

site = Douyutv()
