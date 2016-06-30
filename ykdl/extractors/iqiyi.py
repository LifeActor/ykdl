#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import matchall, match1
from ykdl.extractor import VideoExtractor
from ykdl.compact import compact_bytes

import json
import time
import hashlib

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
def getVMS(tvid, vid):
    t = int(time.time() * 1000)
    src = '76f90cbd92f94a2e925d83e8ccd22cb7'
    key = 'd5fb4bd9d50c4be6948c97edd7254b0e'
    sc = hashlib.new('md5', compact_bytes(str(t) + key  + vid, 'utf-8')).hexdigest()
    vmsreq= url = 'http://cache.m.iqiyi.com/tmts/{0}/{1}/?t={2}&sc={3}&src={4}'.format(tvid,vid,t,sc,src)
    return json.loads(get_content(vmsreq))

class Iqiyi(VideoExtractor):
    name = u"爱奇艺 (Iqiyi)"
    '''
    supported_stream_types = [ 'high', 'standard']

    stream_to_bid = {  '4k': 10, 'fullhd' : 5, 'suprt-high' : 4, 'super' : 3, 'high' : 2, 'standard' :1, 'topspeed' :96}

    stream_2_id = {  '4k': 'BD', 'fullhd' : 'FD', 'suprt-high' : 'OD', 'super' : 'TD', 'high' : 'HD', 'standard' :'SD', 'topspeed' :'LD'}

    stream_2_profile = {  '4k': u'4k', 'fullhd' : u'全高清', 'suprt-high' : u'超高清', 'super' : u'超清', 'high' : u'高清', 'standard' : u'标清', 'topspeed' : u'急速'}
    '''
    non_vip_ids = ['BD', 'FD', 'TD', 'HD', 'SD', 'LD']
    vip_ids = ['vip_h265','vip_h264']
    ids = vip_ids + non_vip_ids
    vd_2_id = {21: 'TD', 2: 'HD', 4: 'FD', 17: 'BD', 96: 'LD', 1: 'SD'}
    vd_2_profile = {21: u'超清', 2: u'高清', 4: u'超高清', 17: u'全高清', 96: u'流畅', 1: u'标清'}



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
            self.title = match1(html, '<title>([^<]+)').split('-')[0]

        tvid, vid = self.vid
        info = getVMS(tvid, vid)
        assert info['code'] == 'A00000', 'can\'t play this video'    

        vip_vids= [info['data']['ctl']['configs']['18']['vid'], info['data']['ctl']['configs']['5']['vid']]
        for v in vip_vids:
            stream_id = self.vip_ids[vip_vids.index(v)]
            vip_info = getVMS(tvid, v)
            vip_url = vip_info['data']['m3u']
            self.stream_types.append(stream_id)
            self.streams[stream_id] = {'video_profile': stream_id, 'container': 'm3u8', 'src': [vip_url], 'size' : 0}        
        
        for stream in info['data']['vidl']:
            stream_id = self.vd_2_id[stream['vd']]
            stream_profile = self.vd_2_profile[stream['vd']]
            self.stream_types.append(stream_id)
            self.streams[stream_id] = {'video_profile': stream_profile, 'container': 'm3u8', 'src': [stream['m3u']], 'size' : 0}
        self.stream_types = sorted(self.stream_types, key = self.ids.index)
    def prepare_list(self):
        html = get_content(self.url)

        return matchall(html, ['data-tvid=\"([^\"]+)\" data-vid=\"([^\"]+)\"'])

site = Iqiyi()
