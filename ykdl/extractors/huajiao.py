#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1
from ykdl.extractor import VideoExtractor
from ykdl.compact import compact_bytes

import uuid
import base64
import json
import time
import random

SID = uuid.uuid4().hex.upper()

class Huajiao(VideoExtractor):
    name = u'huajiao (花椒直播)'

    def prepare(self):
        self.live = True
        html = get_content(self.url)
        self.vid = match1(html, '"sn":"([^"]+)')
        t_a = match1(html, '"keywords" content="([^"]+)')
        self.title = t_a.split(',')[0]
        self.artist = t_a.split(',')[1]

        api_url = 'http://g2.live.360.cn/liveplay?stype=flv&channel=live_huajiao_v2&bid=huajiao&sn={}&sid={}&_rate=xd&ts={}&r={}&_ostype=flash&_delay=0&_sign=null&_ver=13'.format(self.vid, SID, time.time(),random.random())
        encoded_json = get_content(api_url)
        decoded_json = base64.decodestring(compact_bytes(encoded_json[0:3]+ encoded_json[6:], 'utf-8')).decode('utf-8')
        video_data = json.loads(decoded_json)
        real_url = video_data['main']

        self.stream_types.append('current')
        self.streams['current'] = {'container': 'flv', 'video_profile': 'current', 'src' : [real_url], 'size': float('inf')}

site = Huajiao()
