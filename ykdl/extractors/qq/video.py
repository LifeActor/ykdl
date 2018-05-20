#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1, matchall
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
import xml.etree.ElementTree as ET

from ykdl.compact import urlencode, compact_bytes

import random
import base64
import struct
import uuid
import json

PLAYER_PLATFORM = 2
PLAYER_VERSION = '3.2.19.333'
"""
LEGACY FOR REFERENCE ONLY

def pack(data):
    target = []
    target.extend(struct.pack('>I', data[0]))
    target.extend(struct.pack('>I', data[1]))
    target = [c for c in target]
    return target

def unpack(data):
    data = ''.join([chr(b) for b in data])
    target = []
    data = data.encode('latin')
    target.extend(struct.unpack('>I', data[:4]))
    target.extend(struct.unpack('>I', data[4:8]))
    return target

def tea_encrypt(v, key):
    delta = 0x9e3779b9
    s = 0
    v = unpack(v)
    rounds = 16
    while rounds:
        s += delta
        s &= 0xffffffff
        v[0] += (v[1]+s) ^ ((v[1]>>5)+key[1]) ^ ((v[1]<<4)+key[0])
        v[0] &= 0xffffffff
        v[1] += (v[0]+s) ^ ((v[0]>>5)+key[3]) ^ ((v[0]<<4)+key[2])
        v[1] &= 0xffffffff
        rounds = rounds - 1
    return pack(v)

def qq_encrypt(data, key):
    temp = [0x00]*8
    enc = tea_encrypt(data, key)
    for i in range(8, len(data), 8):
        d1 = data[i:]
        for j in range(8):
            d1[j] = d1[j] ^ enc[i+j-8]
        d1 = tea_encrypt(d1, key)
        for j in range(len(d1)):
            d1[j] = d1[j]^data[i+j-8]^temp[j]
            enc.append(d1[j])
            temp[j] = enc[i+j-8]
    return enc

def strsum(data):
    s = 0
    for c in data:
        s = s*131 + ord(c)
    return 0x7fffffff & s

def ccc(platform, version, timestamp):
    key = [1735078436, 1281895718, 1815356193, 879325047]
    s1 = '537e6f0425c50d7a711f4af6af719e05d41d8cd98f00b204e9800998ecf8427e8afc2cf649f5c36c4fa3850ff01c1863d41d8cd98100b204e9810998ecf84271'
    d = [0x3039, 0x02]
    d.append(timestamp)
    d.append(platform)
    d.append(strsum(version))
    d.append(strsum(s1))
    data = [0xa6, 0xf1, 0xd9, 0x2a, 0x82, 0xc8, 0xd8, 0xfe, 0x43]
    for i in d:
        data.extend([c for c in struct.pack('>I', i)])
    data.extend([0x00]*7)
    enc = qq_encrypt(data, key)
    return base64.b64encode(bytes(enc), b'_-').replace(b'=', b'')

def load_key():
    url = 'http://vv.video.qq.com/checktime'
    tree = ET.fromstring(get_content(url))
    t = int(tree.find('./t').text)
    return ccc(PLAYER_PLATFORM, PLAYER_VERSION, t)

"""

def qq_get_final_url(url, vid, fmt_id, filename, fvkey):
    params = {
        'appver': PLAYER_VERSION,
        'otype': 'json',
        'platform': PLAYER_PLATFORM,
        'filename': filename,
        'vid': vid,
        'format': fmt_id,
    }

    content = get_content('http://vv.video.qq.com/getkey?' + urlencode(params))
    data = json.loads(match1(content, r'QZOutputJson=(.+);$'))

    vkey = data.get('key')
    if vkey is None:
        vkey = fvkey

    return "{}{}?vkey={}".format(url, filename, vkey)



class QQ(VideoExtractor):

    name = u"腾讯视频 (QQ)"
    vip = None

    stream_2_id = {
        'fhd': 'BD',
        'shd': 'TD',
        'hd': 'HD',
        'mp4':'HD',
        'flv': 'HD',
        'sd': 'SD',
        'msd':'LD'
    }
    stream_ids = ['BD', 'TD', 'HD', 'SD', 'LD']


    def get_streams_info(self, profile='shd'):
        params = {
            'otype': 'json',
            'platform': PLAYER_PLATFORM,
            'vid': self.vid,
            'defnpayver': 1,
            'appver': PLAYER_VERSION,
            'defn': profile,
        }

        content = get_content('http://vv.video.qq.com/getinfo?' + urlencode(params))
        if profile == 'shd' and '"name":"shd"' not in content and '"name":"fhd"' not in content:
            for infos in self.get_streams_info('hd'):
                yield infos
            return
        else:
            data = json.loads(match1(content, r'QZOutputJson=(.+);$'))
        self.logger.debug('data: ' + str(data))

        video = data['vl']['vi'][0]
        fn = video['fn']
        title = video['ti']
        td = float(video['td'])
        fvkey = video['fvkey']
        # Not to be absolutely accuracy.
        self.vip = video['iflag']

        # Priority for range fetch.
        cdn_url_1 = cdn_url_2 = cdn_url_3 = None
        for cdn in video['ul']['ui']:
            cdn_url = cdn['url']
            # 'video.dispatch.tc.qq.com' supported keep-alive link.
            if cdn_url == 'http://video.dispatch.tc.qq.com/':
                cdn_url_1 = cdn_url
                break
            # IP host.
            if match1(cdn_url, '(^https?://[0-9\.]+/)'):
                cdn_url_3 = cdn_url
            else:
                cdn_url_2 = cdn_url
        cdn_url = cdn_url_1 or cdn_url_2 or cdn_url_3 

        dt = cdn['dt']
        if dt == 1:
            type_name = 'flv'
        elif dt == 2:
            type_name = 'mp4'
        else:
            type_name = 'unknown'

        _num_clips = video['cl']['fc']

        for fmt in data['fl']['fi']:
            fmt_id = fmt['id']
            fmt_name = fmt['name']
            fmt_cname = fmt['cname']
            size = fmt['fs']
            rate = size // td

            fns = fn.split('.')
            fmt_id_num = fmt_id
            fmt_id_prefix = None
            num_clips = 0

            if fmt_id_num > 100000:
                fmt_id_prefix = 'm'
            elif fmt_id_num > 10000:
                fmt_id_prefix = 'p'
                num_clips = _num_clips or 1
            if fmt_id_prefix:
                fmt_id_name = fmt_id_prefix + str(fmt_id_num % 10000)
                if fns[1][0] in ('p', 'm') and not fns[1].startswith('mp'):
                    fns[1] = fmt_id_name
                else:
                    fns.insert(1, fmt_id_name)
            elif fns[1][0] in ('p', 'm') and not fns[1].startswith('mp'):
                del fns[1]

            urls =[]

            if num_clips == 0:
                filename = '.'.join(fns)
                url = qq_get_final_url(cdn_url, self.vid, fmt_id, filename, fvkey)
                urls.append(url)
            else:
                fns.insert(-1, '1')
                for idx in range(1, num_clips+1):
                    fns[-2] = str(idx)
                    filename = '.'.join(fns)
                    url = qq_get_final_url(cdn_url, self.vid, fmt_id, filename, fvkey)
                    if url:
                        urls.append(url)
                    else:
                        self.vip = True
                        break

            yield title, fmt_name, fmt_cname, type_name, urls, size, rate

    def prepare(self):
        info = VideoInfo(self.name)
        if not self.vid:
            self.vid = match1(self.url, 'vid=(\w+)', '/(\w+)\.html')

        if self.vid and match1(self.url, '(^https?://film\.qq\.com)'):
            self.url = 'http://v.qq.com/x/cover/%s.html' % self.vid

        if not self.vid or len(self.vid) != 11:
            html = get_content(self.url)
            self.vid = match1(html, 'vid:\s*[\"\'](\w+)', 'vid\s*=\s*[\"\']\s*(\w+)', 'vid=(\w+)')

            if not self.vid and '<body class="page_404">' in html:
                self.logger.warning('This video has been deleted!')
                return info

        video_rate = {}
        for title, fmt_name, stream_profile, type_name, urls, size, rate in self.get_streams_info():
            stream_id = self.stream_2_id[fmt_name]
            if stream_id not in info.stream_types:
                info.stream_types.append(stream_id)
                info.streams[stream_id] = {'container': type_name, 'video_profile': stream_profile, 'src' : urls, 'size': size}
                video_rate[stream_id] = rate
        info.stream_types = sorted(info.stream_types, key = self.stream_ids.index)
        info.title = title

        # Downloading some videos is very slow, use multithreading range fetch to speed up.
        # Only for video players now.
        info.extra['rangefetch'] = {'first_size': 1024 * 16, 'max_size': 1024 * 32, 'threads': 10, 'video_rate': video_rate}

        if self.vip:
            info.extra['rangefetch']['threads'] = 14
            self.logger.warning('This is a VIP video!')

        return info

    def prepare_list(self):
        html = get_content(self.url)
        vids = [a.strip('"') for a in match1(html, '\"vid\":\[([^\]]+)').split(',')]
        return vids

site = QQ()
