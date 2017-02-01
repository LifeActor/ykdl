#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1, matchall
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo

import json

class Hunantv(VideoExtractor):
    name = u"芒果TV (HunanTV)"

    supported_stream_profile = [ u'蓝光', u'超清', u'高清', u'标清' ]
    supported_stream_types = [ 'BD', 'TD', 'HD', 'SD' ]
    profile_2_types = { u'蓝光': 'BD', u'超清': 'TD', u'高清': 'HD', u'标清': 'SD' }

    def prepare(self):
        info = VideoInfo(self.name)
        if self.url and not self.vid:
            self.vid = match1(self.url, "/([0-9]+).html")

        api_url = 'http://pcweb.api.mgtv.com/player/video?video_id={}'.format(self.vid)
        meta = json.loads(get_content(api_url))

        assert meta['code'] == 200, '[failed] status: {}, msg: {}'.format(meta['status'],meta['msg'])
        assert meta['data'], '[Failed] Video not found.'

        data = meta['data']

        info.title = data['info']['title']
        domain = data['stream_domain'][0]
        for lstream in data['stream']:
            if lstream['url']:
                url = json.loads(get_content(domain + lstream['url']))['info']
                info.streams[self.profile_2_types[lstream['name']]] = {'container': 'm3u8', 'video_profile': lstream['name'], 'src' : [url]}
                info.stream_types.append(self.profile_2_types[lstream['name']])
        info.stream_types= sorted(info.stream_types, key = self.supported_stream_types.index)
        return info

    def prepare_list(self):

        html = get_content(self.url, headers={})

        return matchall(html, ['"a-pic-play" href="([^"]+)"'])

site = Hunantv()
