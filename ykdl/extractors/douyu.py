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

douyu_match_pattern = [ 'class="hroom_id" value="([^"]+)',
                        'data-room_id="([^"]+)'
                      ]
class Douyutv(VideoExtractor):
    name = u'斗鱼 (DouyuTV)'

    stream_ids = ['TD', 'HD', 'SD']
    stream_id_2_rate = {'TD':3 , 'HD':2, 'SD':1}

    def prepare(self):
        info = VideoInfo(self.name, True)
        if self.url:
            self.vid = match1(self.url, '/(\d+)')

        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, '"room_id":(\d+)')
            info.title = match1(html, '<title>([^<]+)').split('-')[0]
        if not info.title:
            info.title = self.name + '-' + str(self.vid)
        tt = int(time.time() / 60)
        did = uuid.uuid4().hex.upper()
        sign_content = '{room_id}{did}A12Svb&%1UUmf@hC{tt}'.format(room_id = self.vid, did = did, tt = tt)
        sign = hashlib.md5(sign_content.encode('utf-8')).hexdigest()

        json_request_url = "http://www.douyu.com/lapi/live/getPlay/%s" % self.vid
        for stream in self.stream_ids:
            payload = {'cdn': 'ws', 'rate': self.stream_id_2_rate[stream], 'tt': tt, 'did': did, 'sign': sign}

            request_form = urlencode(payload)
            html_content = get_content(json_request_url, data = compact_bytes(request_form, 'utf-8'))

            live_data = json.loads(html_content)
            assert live_data['error'] == 0, '%s: live show is not on line or server error!' % self.name
            real_url = live_data['data']['rtmp_url'] + '/' + live_data['data']['rtmp_live']

            info.stream_types.append(stream)
            info.streams[stream] = {'container': 'flv', 'video_profile': 'current', 'src' : [real_url], 'size': float('inf')}
        return info

    def prepare_list(self):

        html = get_content(self.url)
        return matchall(html, douyu_match_pattern)

site = Douyutv()
