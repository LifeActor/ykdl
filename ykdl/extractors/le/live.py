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

    def prepare(self):
        self.live = True
        if not self.vid:
            self.vid = match1(self.url, 'channel=([\d]+)')

        live_data = json.loads(get_content('http://api.live.letv.com/v1/channel/letv/100/1001/{}'.format(self.vid)))['data']

        self.title = self.name + " " + live_data['channelName']

        stream_data = live_data['streams']

        for s in stream_data:
            self.stream_types.append(s['rateType'])
            self.streams[s['rateType']] = {'container': 'm3u8', 'video_profile': s['rateType'], 'size' : float('inf'), 'streamUrl' : s['streamUrl']}

        self.stream_types = sorted(self.stream_types, key = self.supported_stream_types.index)

    def extract_single(self, stream_id):

        date = datetime.datetime.now()

        streamUrl = self.streams[stream_id]['streamUrl'] + '&format=1&expect=2&termid=1&hwtype=un&platid=10&splatid=1001&playid=1sign=live_web&&ostype={}&p1=1&p2=10&p3=-&vkit={}&station={}&tm={}'.format(platform.platform(), date.strftime("%Y%m%d"), self.vid, int(time.time()))

        data = json.loads(get_content(streamUrl))

        self.streams[stream_id]['src'] = [data['location']]

    def extract(self):
        if not self.param.info:
            stream_id = self.param.format or self.stream_types[0]
            self.extract_single(stream_id)
        else:
            for stream_id in self.stream_types:
                self.extract_single(stream_id)

site = LeLive()
        
