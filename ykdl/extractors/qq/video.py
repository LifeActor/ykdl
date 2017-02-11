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
import os

PLAYER_PLATFORM = 1
PLAYER_VERSION = '3.2.18.286'
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

def qq_get_final_url(url, fmt_name, type_name, br, form, fn):

    content = get_content('http://vv.video.qq.com/getkey',data=compact_bytes(form, 'utf-8'), charset = 'ignore')
    tree = ET.fromstring(content)

    vkey = tree.find('./key').text
    level = tree.find('./level').text
    sp = tree.find('./sp').text

    params = {
        'stdfrom': 'v1090',
        'type': type_name,
        'vkey': vkey,
        'level': level,
        'platform': PLAYER_PLATFORM,
        'br': br,
        'fmt': fmt_name,
        'sp': sp,
    }
    form = urlencode(params)
    return "%s?%s" % (url, form)



class QQ(VideoExtractor):

    name = u"腾讯视频 (QQ)"

    supported_stream_types = [ 'shd', 'mp4', 'hd', 'sd' ]

    stream_2_profile = { 'shd': u'超清', 'mp4': u'高清mp4', 'hd': u'高清', 'flv': u'高清flv', 'sd': u'标清' }

    stream_2_id = { 'shd': 'TD', 'mp4': 'HD', 'hd': 'HD', 'flv': 'HD', 'sd': 'SD' }

    stream_ids = ['TD', 'HD', 'SD']


    def get_stream_info(self, profile):


        player_pid = uuid.uuid4().hex.upper()

        params = {
            'fp2p': 1,
            'pid': player_pid,
            'otype': 'xml',
            'defn': profile,
            'platform': 1,
            'fhdswitch': 0,
            'charge': 0,
            'ckey' : "",
            'vid': self.vid,
            'defnpayver': 1,
            'encryptVer': "",
            'speed': random.randint(512, 1024),
            'ran': random.random(),
            'appver': PLAYER_VERSION,
            'defaultfmt': profile,
            'utype': -1,
            'vids': self.vid
        }

        form = urlencode(params)
        content = get_content('http://vv.video.qq.com/getinfo',data=compact_bytes(form, 'utf-8'), charset = 'ignore')
        tree = ET.fromstring(content)
        fmt_id = None
        fmt_name = None
        fmt_br = None
        for fmt in tree.findall('./fl/fi'):
            sl = int(fmt.find('./sl').text)
            if sl:
                fmt_id = fmt.find('./id').text
                fmt_name = fmt.find('./name').text
                fmt_br = fmt.find('./br').text

        video = tree.find('./vl/vi')
        filename = video.find('./fn').text
        title = video.find('./ti').text

        cdn = video.find('./ul/ui')
        cdn_url = cdn.find('./url').text
        filetype = int(cdn.find('./dt').text)
        vt = cdn.find('./vt').text
        if filetype == 1:
            type_name = 'flv'
        elif filetype == 2:
            type_name = 'mp4'
        else:
            type_name = 'unknown'

        num_clips = len(video.findall('./cl/ci'))
        size = int(video.find('./fs').text)

        fns = os.path.splitext(filename)

        #may have preformence issue when info_only
        urls =[]

        if num_clips == 0:
            params = {
                'ran': random.random(),
                'appver': PLAYER_VERSION,
                'otype': 'xml',
                'encryptVer': "",
                'platform': 1,
                'filename': filename,
                'vid': self.vid,
                'vt': vt,
                'charge': 0,
                'format': fmt_id,
                'cKey': "",
            }

            form = urlencode(params)
            clip_url = '%s%s' % (cdn_url, filename)
            urls.append(qq_get_final_url(clip_url, fmt_name, type_name, fmt_br, form, filename))

        else:
            for idx in range(1, num_clips+1):
                fn = '%s.%d%s' % (fns[0], idx, fns[1])
                params = {
                    'ran': random.random(),
                    'appver': PLAYER_VERSION,
                    'otype': 'xml',
                    'encryptVer': "",
                    'platform': 1,
                    'filename': fn,
                    'vid': self.vid,
                    'vt': vt,
                    'charge': 0,
                    'format': fmt_id,
                    'cKey': "",
                }
                form = urlencode(params)
                clip_url = '%s%s' % (cdn_url, fn)
                urls.append(qq_get_final_url(clip_url, fmt_name, type_name, fmt_br, form, fn))

        return title, fmt_name, type_name, urls, size

    def prepare(self):
        info = VideoInfo(self.name)
        if not self.vid:
            self.vid = match1(self.url, '/(\w+)\.html','vid=(\w+)')

        if not self.vid or len(self.vid) != 11:
            html = get_content(self.url)
            self.vid = match1(html, 'vid:\s*\"([^\"]+)', 'vid\s*=\s*"\s*([^"]+)"', 'vid=(\w+)')

        for stream in self.supported_stream_types:
            title, fmt_name, type_name, urls, size = self.get_stream_info(stream)
            stream_id = self.stream_2_id[fmt_name]
            stream_profile = self.stream_2_profile[fmt_name]
            if not stream_id in info.stream_types:
                info.stream_types.append(stream_id)
                info.streams[stream_id] = {'container': type_name, 'video_profile': stream_profile, 'src' : urls, 'size': size}
        info.stream_types = sorted(info.stream_types, key = self.stream_ids.index)
        info.title = title
        return info

    def prepare_list(self):
        html = get_content(self.url)
        vids = [a.strip('"') for a in match1(html, '\"vid\":\[([^\]]+)').split(',')]
        return vids

site = QQ()
