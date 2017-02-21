#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .youkujs import *
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.util.html import get_content

import json
import base64, time

class Acorig(VideoExtractor):
    name = u"AcFun 优酷合作视频"

    client_id = '908a519d032263f8'
    ct = 85
    refer = 'http://cdn.aixifan.com/player/sslhomura/AcFunV3Player170213.swf'
    key = "328f45d8"

    def get_custom_stream(self):

        api = "http://aauth-vod.cn-beijing.aliyuncs.com/acfun/web?vid={}&ct={}&time={}".format(self.vid, self.ct,int(time.time()*1000))
        data = rc4(self.key, base64.b64decode(json.loads(get_content(api, charset='utf-8'))['data']))
        self.stream_data = json.loads(data)['stream']

    def setup(self, info):

        self.vid, self.embsig = self.vid

        info.title = self.name + "-" + self.vid

        install_acode('v', 'b', '1z4i', '86rv', 'ogb', 'ail')
        self.get_custom_stream()

    def prepare(self):
        info = VideoInfo(self.name)
        self.setup(info)
        for s in self.stream_data:
            if 'segs' in s:
                stream_type = stream_code_to_id[s['stream_type']]
                stream_urls = [seg['url'] for seg in s['segs']]
                info.stream_types.append(stream_type)
                info.streams[stream_type] = {'container': 'mp4', 'video_profile': stream_code_to_profiles[stream_type], 'src': stream_urls, 'size' : 0}
        info.stream_types = sorted(info.stream_types, key=ids.index)
        return info

site = Acorig()
