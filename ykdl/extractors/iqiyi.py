#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import matchall, match1
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.compact import compact_bytes
from ykdl.util import log
from .iqiyi_sc import gen_sc

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

def geth5VMS(tvid, vid, rate):
    t = int(time.time() * 1000)
    sc = gen_sc(tvid, t).decode('utf-8')
    vmsreq= 'http://cache.m.iqiyi.com/jp/tmts/{}/{}/?platForm=h5&rate={}&tvid={}&vid={}&cupid=qc_100001_100186&type=mp4&olimit=0&agenttype=13&src=d846d0c32d664d32b6b54ea48997a589&sc={}&t={}&__jsT=null'.format(tvid, vid, rate, tvid, vid, sc, t - 7)
    return json.loads(get_content(vmsreq)[13:])

class Iqiyi(VideoExtractor):
    name = u"爱奇艺 (Iqiyi)"
    '''
    supported_stream_types = [ 'high', 'standard']

    stream_to_bid = {  '4k': 10, 'fullhd' : 5, 'suprt-high' : 4, 'super' : 3, 'high' : 2, 'standard' :1, 'topspeed' :96}

    stream_2_id = {  '4k': 'BD', 'fullhd' : 'FD', 'suprt-high' : 'OD', 'super' : 'TD', 'high' : 'HD', 'standard' :'SD', 'topspeed' :'LD'}

    stream_2_profile = {  '4k': u'4k', 'fullhd' : u'全高清', 'suprt-high' : u'超高清', 'super' : u'超清', 'high' : u'高清', 'standard' : u'标清', 'topspeed' : u'急速'}
    '''
    ids = ['4k','BD', 'TD', 'HD', 'SD', 'LD']
    vd_2_id = {10: '4k', 19: '4k', 5:'BD', 18: 'BD', 14: 'HD', 21: 'HD', 2: 'HD', 4: 'TD', 17: 'TD', 96: 'LD', 1: 'SD'}
    id_2_profile = {'4k':'4k', 'BD': '1080p','TD': '720p', 'HD': '540p', 'SD': '360p', 'LD': '210p'}
    id_ignore = [19, 18, 21, 17]

    id_h5 = [2, 1]



    def prepare(self):
        info = VideoInfo(self.name)
        if self.url and not self.vid:
            vid = matchall(self.url, ['curid=([^_]+)_([\w]+)'])
            if vid:
                self.vid = vid[0]

        if self.url and not self.vid:
            html = get_content(self.url)
            tvid = match1(html, 'data-player-tvid="([^"]+)"', 'tvid=([^&]+)' , 'tvId:([^,]+)')
            videoid = match1(html, 'data-player-videoid="([^"]+)"', 'vid=([^&]+)', 'vid:"([^"]+)')
            self.vid = (tvid, videoid)
            info.title = match1(html, '<title>([^<]+)').split('-')[0]

        tvid, vid = self.vid
        data = getVMS(tvid, vid)
        if not data['code'] == 'A00000':
            for bid in self.id_h5:
                h5_data = geth5VMS(tvid, vid, bid)
                if h5_data["code"] == "A00000":
                    stream = self.vd_2_id[bid]
                    profile = self.id_2_profile[stream]
                    info.title = h5_data['data']['playInfo']['vn']
                    info.stream_types.append(stream)
                    info.streams[stream] = {'container': 'mp4', 'video_profile': profile, 'src' : [h5_data['data']['m3u']], 'size' : 0}
            return info

        for stream in data['data']['vidl']:
            try:
                stream_id = self.vd_2_id[stream['vd']]
                if stream_id in info.stream_types or stream_id in self.id_ignore:
                    continue
                stream_profile = self.id_2_profile[stream_id]
                info.stream_types.append(stream_id)
                info.streams[stream_id] = {'video_profile': stream_profile, 'container': 'm3u8', 'src': [stream['m3u']], 'size' : 0}
            except:
                log.i("vd: {} is not handled".format(stream['vd']))
                log.i("info is {}".format(stream))

        # why I need do below???
        try:
            vip_vds = data['data']['ctl']['vip']['bids']
            vip_conf = data['data']['ctl']['configs']
        except:
            info.stream_types = sorted(info.stream_types, key = self.ids.index)
            return info

        if not 'BD' in info.stream_types:
            p1080_vids = []
            if 5 in vip_vds:
                p1080_vids.append(vip_conf['5']['vid'])
            for v in p1080_vids:
                p1080_info = getVMS(tvid, v)
                if p1080_info['code'] == 'A00000':
                    p1080_url = p1080_info['data']['m3u']
                    info.stream_types.append('BD')
                    info.streams['BD'] = {'video_profile': '1080p', 'container': 'm3u8', 'src': [p1080_url], 'size' : 0}
                    break

        if not '4k' in info.stream_types:
            k4_vids = []
            if 10 in vip_vds:
                k4_vids.append(vip_conf['10']['vid'])
            for v in k4_vids:
                k4_info = getVMS(tvid, v)
                if k4_info['code'] == 'A00000':
                    k4_url = k4_info['data']['m3u']
                    info.stream_types.append('4k')
                    info.streams['4k'] = {'video_profile': '4k', 'container': 'm3u8', 'src': [k4_url], 'size' : 0}
                    break

        info.stream_types = sorted(info.stream_types, key = self.ids.index)
        return info

    def prepare_list(self):
        html = get_content(self.url)

        return matchall(html, ['data-tvid=\"([^\"]+)\" data-vid=\"([^\"]+)\"'])

site = Iqiyi()
