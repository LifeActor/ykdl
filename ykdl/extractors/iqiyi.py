#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import matchall, match1
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.compact import urlencode, compact_bytes

import json
import time
import hashlib
import random

macid = None

def get_macid():
    '''获取macid,此值是通过mac地址经过算法变换而来,对同一设备不变'''
    global macid
    if macid is None:
        macid = ''
        chars = 'abcdefghijklnmopqrstuvwxyz0123456789'
        size = len(chars)
        for i in range(32):
            macid += list(chars)[random.randint(0,size-1)]
    return macid

def md5(s):
    return hashlib.md5(compact_bytes(s, 'utf8')).hexdigest()

def md5x(s):
    #sufix = ''
    #for j in range(8):
    #    for k in range(4):
    #        v4 = 13 * (66 * k + 27 * j) % 35
    #        if ( v4 >= 10 ):
    #            v8 = v4 + 88
    #        else:
    #            v8 = v4 + 49
    #        sufix += chr(v8)
    return md5(s + '1j2k2k3l3l4m4m5n5n6o6o7p7p8q8q9r')

def cmd5x(s):
    # the param src below uses salt h2l6suw16pbtikmotf0j79cej4n8uw13
    #    01010031010000000000
    #    01010031010010000000
    #    01080031010000000000
    #    01080031010010000000
    #    03020031010000000000
    #    03020031010010000000
    #    03030031010000000000
    #    03030031010010000000
    #    02020031010000000000
    #    02020031010010000000
    return md5(s + 'h2l6suw16pbtikmotf0j79cej4n8uw13')

def getdash(tvid, vid, bid=500):
    tm = int(time.time() * 1000)
    host = 'https://cache.video.iqiyi.com'
    params = {
        'tvid': tvid,
        'bid': bid,
        'vid': vid,
        'src': '01010031010000000000',
        'vt': 0,
        'rs': 1,
        'uid': '',
        'ori': 'pcw',
        'ps': 0,
        'tm': tm,
        'qd_v': 1,
        'k_uid': get_macid(),
        'pt': 0,
        'd': 0,
        's': '',
        'lid': '',
        'cf': '',
        'ct': '',
        'authKey': cmd5x('0{}{}'.format(tm, tvid)),
        'k_tag': 1,
        'ost': 0,
        'ppt': 0,
        'locale': 'zh_cn',
        'pck': '',
        'k_err_retries': 0,
        'ut': 0
    }
    src = '/dash?{}'.format(urlencode(params))
    vf = cmd5x(src)
    req_url = '{}{}&vf={}'.format(host, src, vf)
    html = get_content(req_url)
    return json.loads(html)

def getvps(tvid, vid):
    tm = int(time.time() * 1000)
    host = 'http://cache.video.qiyi.com'
    params = {
        'tvid': tvid,
        'vid': vid,
        'v': 0,
        'qypid': '{}_12'.format(tvid),
        'src': '01012001010000000000',
        't': tm,
        'k_tag': 1,
        'k_uid': get_macid(),
        'rs': 1,
    }
    src = '/vps?{}'.format(urlencode(params))
    vf = md5x(src)
    req_url = '{}{}&vf={}'.format(host, src, vf)
    html = get_content(req_url)
    return json.loads(html)

class Iqiyi(VideoExtractor):
    name = u"爱奇艺 (Iqiyi)"

    ids = ['4k','BD', 'TD', 'HD', 'SD', 'LD']
    vd_2_id = dict(sum([[(vd, id) for vd in vds] for id, vds in {
        '4k': [10, 19],
        'BD': [5, 18, 600],
        'TD': [4, 17, 500],
        'HD': [2, 14, 21, 300],
        'SD': [1, 200],
        'LD': [96, 100]
    }.items()], []))
    id_2_profile = {
        '4k': '4k',
        'BD': '1080p',
        'TD': '720p',
        'HD': '540p',
        'SD': '360p',
        'LD': '210p'
    }

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
                tvid = match1(html,
                              'data-player-tvid="([^"]+)"',
                              'tvid="(.+?)"',
                              'tvId:([^,]+)',
                              r'''param\['tvid'\]\s*=\s*"(.+?)"''',
                              r'"tvid":\s*"(\d+)"')
                videoid = match1(html,
                                'data-player-videoid="([^"]+)"',
                                'vid="(.+?)"',
                                'vid:"([^"]+)',
                                r'''param\['vid'\]\s*=\s*"(.+?)"''',
                                r'"vid":\s*"(\w+)"')
                self.vid = (tvid, videoid)
                info.title = match1(html, '<title>([^<]+)').split('-')[0]

        tvid, vid = self.vid

        def push_stream(bid, container, fs_array, size):
            real_urls = []
            for seg_info in fs_array:
                url = url_prefix + seg_info['l']
                json_data = json.loads(get_content(url))
                down_url = json_data['l']
                real_urls.append(down_url)
            stream = self.vd_2_id[bid]
            info.stream_types.append(stream)
            stream_profile = self.id_2_profile[stream]
            info.streams[stream] = {
                'video_profile': stream_profile,
                'container': container,
                'src': real_urls,
                'size': size
            }

        try:
            # try use vps firt
            vps_data = getvps(tvid, vid)
            assert vps_data['code'] == 'A00000', 'can\'t play this video!!'
            url_prefix = vps_data['data']['vp']['du']
            vs_array = vps_data['data']['vp']['tkl'][0]['vs']
            for vs in vs_array:
                bid = vs['bid']
                fs_array = vs['fs']
                size = vs['vsize']
                push_stream(bid, 'flv', fs_array, size)

        except:
            # use dash as fallback
            dash_data = getdash(tvid, vid)
            assert dash_data['code'] == 'A00000', 'can\'t play this video!!'
            url_prefix = dash_data['data']['dd']
            streams = dash_data['data']['program']['video']
            for stream in streams:
                if 'fs' in stream:
                    bid = stream['bid']
                    container = stream['ff']
                    fs_array = stream['fs']
                    size = stream['vsize']
                    break
            push_stream(bid, container, fs_array, size)

        info.stream_types = sorted(info.stream_types, key=self.ids.index)
        return info

    def prepare_list(self):
        html = get_content(self.url)

        return matchall(html, ['data-tvid=\"([^\"]+)\" data-vid=\"([^\"]+)\"'])

site = Iqiyi()
