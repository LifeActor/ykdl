#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import matchall, match1
from ykdl.extractor import VideoExtractor

import json
import time

from .iqiyi_sc import gen_sc

'''
com.qiyi.player.core.model.def.DefinitonEnum
bid meaning for quality
0 none
1 standard
2 high
3 super
4 suprt-high
5 fullhd
10 4k
96 topspeed
'''

class Iqiyi(VideoExtractor):
    name = u"爱奇艺 (Iqiyi)"

    supported_stream_types = [ 'high', 'standard']

    stream_to_bid = {  '4k': 10, 'fullhd' : 5, 'suprt-high' : 4, 'super' : 3, 'high' : 2, 'standard' :1, 'topspeed' :96}

    stream_2_id = {  '4k': 'BD', 'fullhd' : 'FD', 'suprt-high' : 'OD', 'super' : 'TD', 'high' : 'HD', 'standard' :'SD', 'topspeed' :'LD'}

    stream_2_profile = {  '4k': u'4k', 'fullhd' : u'全高清', 'suprt-high' : u'超高清', 'super' : u'超清', 'high' : u'高清', 'standard' : u'标清', 'topspeed' : u'急速'}

    ids = ['BD', 'FD', 'OD', 'TD', 'HD', 'SD', 'LD']

    def getVMS(self, rate):
        tvid, vid = self.vid
        t = int(time.time() * 1000)
        sc = gen_sc(tvid, t).decode('utf-8')
        vmsreq= 'http://cache.m.iqiyi.com/jp/tmts/{}/{}/?platForm=h5&rate={}&tvid={}&vid={}&cupid=qc_100001_100186&type=mp4&olimit=0&agenttype=13&src=d846d0c32d664d32b6b54ea48997a589&sc={}&t={}&__jsT=null'.format(tvid, vid, rate, tvid, vid, sc, t - 7)
        return json.loads(get_content(vmsreq)[13:])

    def prepare(self):

        if self.url and not self.vid:
            vid = matchall(self.url, ['curid=([^_]+)_([\w]+)'])
            if vid:
                self.vid = vid[0]

        if self.url and not self.vid:
            html = get_content(self.url)
            tvid = match1(html, 'data-player-tvid="([^"]+)"') or match1(self.url, 'tvid=([^&]+)')
            videoid = match1(html, 'data-player-videoid="([^"]+)"') or match1(self.url, 'vid=([^&]+)')
            self.vid = (tvid, videoid)

        for stream in self.supported_stream_types:
            info = self.getVMS(self.stream_to_bid[stream])
            if info["code"] == "A00000":
                stream_id = self.stream_2_id[stream]
                stream_profile = self.stream_2_profile[stream]
                self.title = info['data']['playInfo']['vn']
                self.stream_types.append(stream_id)
                self.streams[stream_id] = {'container': 'mp4', 'video_profile': stream_profile, 'src' : [info['data']['m3u']], 'size' : 0}

    def prepare_list(self):
        html = get_content(self.url)

        return matchall(html, ['data-tvid=\"([^\"]+)\" data-vid=\"([^\"]+)\"'])

site = Iqiyi()
