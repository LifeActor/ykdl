#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.match import match1
from ykdl.util.html import get_content
from ykdl.extractor import VideoExtractor

import time
import json

class LongzhuLive(VideoExtractor):
    name = u'Longzhu Live (龙珠直播)'

    supported_stream_types = ['SD', 'HD', 'TD', 'BD']
    types_2_profile = {'SD': '标清', 'HD':'高清', 'TD':'超清', 'BD':'原画'}

    def prepare(self):
        self.live = True

        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, 'roomid: (\d+)')
            self.title = match1(html, '"title":"([^"]+)')
            self.artist = match1(html, '"Name":"([^"]+)')

        api_url = 'http://livestream.plu.cn/live/getlivePlayurl?roomId={}&{}'.format(self.vid, int(time.time()))

        data = json.loads(get_content(api_url))['playLines'][0]['urls'] #don't know index 1

        for i in data:
            if i['ext'] == 'flv':
                stream_id = self.supported_stream_types[i['rateLevel'] -1]
                self.stream_types.append(stream_id)
                self.streams[stream_id] = {'container': 'flv', 'video_profile': self.types_2_profile[stream_id], 'src' : [i['securityUrl']], 'size': 0}

        #sort stream_types
        types = self.supported_stream_types
        types.reverse()
        self.stream_types = sorted(self.stream_types, key=types.index)

site = LongzhuLive()
