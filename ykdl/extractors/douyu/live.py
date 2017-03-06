#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1, matchall
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.compact import urlencode,compact_bytes

from hashlib import md5
import time
import json
import uuid

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
        if self.url:
            self.vid = match1(self.url, '/(\d+)')

        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, '"room_id.?":(\d+)')

        for stream in self.stream_ids:
            tt = int(time.time())
            rate = self.stream_id_2_rate[stream]
            signContent = 'lapi/live/thirdPart/getPlay/{}?aid=pcclient&rate={}&time={}9TUk5fjjUjg9qIMH3sdnh'.format(self.vid, rate , tt)
            sign = md5(signContent.encode('utf-8')).hexdigest()
            url = 'http://coapi.douyucdn.cn/lapi/live/thirdPart/getPlay/{}?rate={}'.format(self.vid, rate)

            html_content = get_content(url, headers = {		'auth': sign, 'time': str(tt), 'aid': 'pcclient' })
            live_data = json.loads(html_content)['data']

            real_url = live_data['live_url']

            info.stream_types.append(stream)
            info.streams[stream] = {'container': 'flv', 'video_profile': self.id_2_profile[stream], 'src' : [real_url], 'size': float('inf')}
            info.title = live_data['room_name']
        return info

    def prepare_list(self):

        html = get_content(self.url)
        return matchall(html, douyu_match_pattern)

site = Douyutv()
