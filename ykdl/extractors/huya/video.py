#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.extractor import VideoExtractor
from ykdl.util.html import get_content
from ykdl.util.match import match1

import json

class HuyaVideo(VideoExtractor):
    name = "huya video (虎牙视频)"

    supported_stream_types = ['原画', '超清', '高清', '流畅']

    def prepare(self):

        if not self.vid:
            self.vid = match1(self.url, 'play/(\d+).html')

        api_url = 'http://playapi.v.duowan.com/index.php?vid={}&partner=&r=play%2Fvideo'.format(self.vid)
        data = json.loads(get_content(api_url))['result']['items']
        #lazy title
        self.title = self.name + '_' + self.vid

        for i in data:
            d = i['transcode']
            self.stream_types.append(i['task_name'])
            self.streams[i['task_name']] = {'container': 'mp4', 'src': [d['urls'][0]], 'size' : int(d['size'])}

        self.stream_types = sorted(self.stream_types, key = self.supported_stream_types.index)        

site = HuyaVideo()
