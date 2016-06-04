#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.match import match1
from ykdl.util.html import get_content
from ykdl.extractor import VideoExtractor

import time
import json

class LongzhuLive(VideoExtractor):
    name = u'Longzhu Live (龙珠直播)'

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
                self.stream_types.append("current")
                self.streams["current"] = {'container': 'flv', 'video_profile': 'current', 'src' : [i['securityUrl']], 'size': 0}

site = LongzhuLive()
