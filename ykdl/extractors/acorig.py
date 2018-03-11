#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .youkujs import *
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.util.html import get_content, add_header

import json
import base64, time

class Acorig(VideoExtractor):
    name = u"AcFun 优酷合作视频"

    client_id = '908a519d032263f8'
    ct = 85
    refer = 'http://player-vod.cn-beijing.aliyuncs.com/player/2017030915/core/cloud.swf'
    key = "8bdc7e1a"

    def prepare(self):
        info = VideoInfo(self.name)
        add_header('User-Agent', "abcd")
        add_header('Referer', "http://acfun.cn/")
        self.vid, self.embsig = self.vid

        api = "http://player.acfun.cn/flash_data?vid={}&ct={}&ev=3&sign={}&time={}".format(self.vid, self.ct, self.embsig, int(time.time()*1000))
        data = rc4(self.key, base64.b64decode(json.loads(get_content(api, charset='utf-8'))['data']))
        stream_data = json.loads(data)
        info.title = stream_data['video']['title']
        for s in stream_data['stream']:
            if 'segs' in s:
                stream_type = stream_code_to_id[s['stream_type']]
                stream_urls = [seg['url'] for seg in s['segs']]
                size = s['total_size']
                info.stream_types.append(stream_type)
                info.streams[stream_type] = {'container': 'mp4', 'video_profile': stream_code_to_profiles[stream_type], 'src': stream_urls, 'size' : size}
        info.stream_types = sorted(info.stream_types, key=ids.index)
        info.extra['ua'] = 'abcd'
        return info

site = Acorig()
