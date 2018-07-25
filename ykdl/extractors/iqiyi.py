#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import matchall, match1
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo

import json
import time
import hashlib
import random

def get_macid():
    '''获取macid,此值是通过mac地址经过算法变换而来,对同一设备不变'''
    macid=''
    chars = 'abcdefghijklnmopqrstuvwxyz0123456789'
    size = len(chars)
    for i in range(32):
        macid += list(chars)[random.randint(0,size-1)]
    return macid

def get_vf(url_params):
    '''计算关键参数vf'''
    sufix=''
    for j in range(8):
        for k in range(4):
            v4 = 13 * (66 * k + 27 * j) % 35
            if ( v4 >= 10 ):
                v8 = v4 + 88
            else:
                v8 = v4 + 49
            sufix += chr(v8)
    url_params += sufix
    m = hashlib.md5()
    m.update(url_params.encode('utf-8'))
    vf = m.hexdigest()
    return vf

def getvps(tvid, vid):
    tm = int(time.time() * 1000)
    host = 'http://cache.video.qiyi.com'
    src='/vps?tvid='+tvid+'&vid='+vid+'&v=0&qypid='+tvid+'_12&src=01012001010000000000&t='+str(tm)+'&k_tag=1&k_uid='+get_macid()+'&rs=1'
    vf = get_vf(src)
    req_url = host + src + '&vf=' + vf
    html = get_content(req_url)
    return json.loads(html)

class Iqiyi(VideoExtractor):
    name = u"爱奇艺 (Iqiyi)"

    ids = ['4k','BD', 'TD', 'HD', 'SD', 'LD']
    vd_2_id = {10: '4k', 19: '4k', 5:'BD', 18: 'BD', 14: 'HD', 21: 'HD', 2: 'HD', 4: 'TD', 17: 'TD', 96: 'LD', 1: 'SD'}
    id_2_profile = {'4k':'4k', 'BD': '1080p','TD': '720p', 'HD': '540p', 'SD': '360p', 'LD': '210p'}

    def prepare(self):
        info = VideoInfo(self.name)
        if self.url and not self.vid:
            vid = matchall(self.url, ['curid=([^_]+)_([\w]+)'])
            if vid:
                self.vid = vid[0]
                info_u = 'http://mixer.video.iqiyi.com/jp/mixin/videos/' + self.vid[0]
                mixin = get_content(info_u)
                mixin_json = json.loads(mixin[len('var tvInfoJs='):])
                real_u = mixin_json['url']
                real_html = get_content(real_u)
                info.title = match1(real_html, '<title>([^<]+)').split('-')[0]

        if self.url and not self.vid:
            html = get_content(self.url)
            video_info = match1(html, ":video-info='(.+?)'")
            if video_info:
                video_info = json.loads(video_info)
                self.vid = str(video_info['tvId']), str(video_info['vid'])
                info.title = video_info['name']
            else:

                tvid = match1(html, 'data-player-tvid="([^"]+)"', 'tvid="(.+?)"', 'tvId:([^,]+)', r'''param\['tvid'\]\s*=\s*"(.+?)"''', r'"tvid":\s*"(\d+)"')
                videoid = match1(
                    html, 'data-player-videoid="([^"]+)"', 'vid="(.+?)"', 'vid:"([^"]+)', r'''param\['vid'\]\s*=\s*"(.+?)"''', r'"vid":\s*"(\w+)"')
                self.vid = (tvid, videoid)
                info.title = match1(html, '<title>([^<]+)').split('-')[0]

        tvid, vid = self.vid
        vps_data = getvps(tvid, vid)
        assert vps_data['code'] == 'A00000', 'can\'t play this video!!'
        url_prefix = vps_data['data']['vp']['du']
        stream = vps_data['data']['vp']['tkl'][0]
        vs_array = stream['vs']
        for vs in vs_array:
            bid = vs['bid']
            fs_array = vs['fs']
            real_urls = []
            for seg_info in fs_array:
                url = url_prefix + seg_info['l']
                json_data=json.loads(get_content(url))
                down_url = json_data['l']
                real_urls.append(down_url)
            stream = self.vd_2_id[bid]
            info.stream_types.append(stream)
            stream_profile = self.id_2_profile[stream]
            info.streams[stream] = {'video_profile': stream_profile, 'container': 'flv', 'src': real_urls, 'size' : 0}
        info.stream_types = sorted(info.stream_types, key = self.ids.index)
        return info

    def prepare_list(self):
        html = get_content(self.url)

        return matchall(html, ['data-tvid=\"([^\"]+)\" data-vid=\"([^\"]+)\"'])

site = Iqiyi()
