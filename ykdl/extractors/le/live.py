#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import datetime
import platform


from ykdl.util.html import get_content, url_info
from ykdl.util.match import match1, matchall
from ykdl.extractor import VideoExtractor


class LeLive(VideoExtractor):
    name = u"Le Live (乐视轮播)"

    supported_stream_types = ['flv_1080p3m', 'flv_1080p', 'flv_1300', 'flv_1000', 'flv_720p', 'flv_350']

    stream_2_profile = {'flv_1080p3m': u'1080p' ,'flv_1080p': u'1080p' , 'flv_1300': u'超清', 'flv_1000': u'高清' , 'flv_720p': u'标清', 'flv_350': u'流畅' }

    stream_2_id = {'flv_1080p3m': 'BD', 'flv_1080p': 'BD' , 'flv_1300': 'TD', 'flv_1000': 'HD' , 'flv_720p': 'SD', 'flv_350': 'LD' }

    stream_ids = ['BD', 'TD', 'HD', 'SD', 'LD']

    def prepare(self):
        self.live = True
        if not self.vid:
            self.vid = match1(self.url, 'channel=([\d]+)')

        live_data = json.loads(get_content('http://api.live.letv.com/v1/channel/letv/100/1001/{}'.format(self.vid)))['data']

        self.title = self.name + " " + live_data['channelName']

        stream_data = live_data['streams']

        for s in stream_data:
            stream_id = self.stream_2_id[s['rateType']]
            stream_profile = self.stream_2_profile[s['rateType']]
            if not stream_id in self.stream_types:
                self.stream_types.append(stream_id)
                self.streams[stream_id] = {'container': 'm3u8', 'video_profile': stream_profile, 'size' : float('inf'), 'streamUrl' : s['streamUrl']}

        self.stream_types = sorted(self.stream_types, key = self.stream_ids.index)

    def extract_single(self, stream_id):

        date = datetime.datetime.now()

        streamUrl = self.streams[stream_id]['streamUrl'] + '&format=1&expect=2&termid=1&hwtype=un&platid=10&splatid=1001&playid=1sign=live_web&&ostype={}&p1=1&p2=10&p3=-&vkit={}&station={}&tm={}'.format(platform.platform(), date.strftime("%Y%m%d"), self.vid, int(time.time()))

        data = json.loads(get_content(streamUrl))

        self.streams[stream_id]['src'] = [data['location']]

    def extract(self):
        for stream_id in self.stream_types:
            self.extract_single(stream_id)

site = LeLive()
        
