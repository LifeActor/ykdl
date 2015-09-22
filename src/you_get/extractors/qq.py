#!/usr/bin/env python

from ..common import *
from ..extractor import VideoExtractor

import xml.etree.ElementTree as ET
import urllib.parse
import random
import base64
import struct
import uuid

PLAYER_PLATFORM = 11
PLAYER_VERSION = '3.2.19.333'
KLIB_VERSION = '2.0'

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

def get_from(url):
    return 'v1001'

def qq_get_final_url(url, fmt_name, type_name, br, sp, vkey, level):
    params = {
        'stdfrom': get_from(url),
        'type': type_name,
        'vkey': vkey,
        'level': level,
        'platform': PLAYER_PLATFORM,
        'br': br,
        'fmt': fmt_name,
        'sp': sp,
    }
    form = urllib.parse.urlencode(params)
    return "%s?%s" % (url, form)

def load_key():
    url = 'http://vv.video.qq.com/checktime'
    tree = ET.fromstring(get_content(url))
    t = int(tree.find('./t').text)
    return ccc(PLAYER_PLATFORM, PLAYER_VERSION, t)

class QQ(VideoExtractor):

    name = "腾讯视频 (QQ)"

    supported_stream_types = [ 'shd', 'hd', 'sd' ]

    stream_2_profile = { 'shd': '超清', 'hd': '高清', 'sd': '标清' }


    def get_stream_info(self, profile):


        player_pid = uuid.uuid4().hex.upper()

        player_guid = uuid.uuid4().hex.upper()

        params = {
            'vids': self.vid,
            'vid': self.vid,
            'otype': 'xml',
            'defnpayver': 1,
            'platform': PLAYER_PLATFORM,
            'charge': 0,
            'ran': random.random(),
            'speed': random.randint(1024, 4096),
            'pid': player_pid,
            'guid': player_guid,
            'appver': PLAYER_VERSION,
            'fhdswitch': 0,
            'defn': profile,
            'defaultfmt': profile,
            'fp2p': 1,
            'utype': 0,
            'cKey': load_key(),
            'encryptVer': KLIB_VERSION,
        }

        form = urllib.parse.urlencode(params)
        info_url = '%s?%s' % ('http://vv.video.qq.com/getvinfo', form)
        content = get_content(info_url)

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

        clips = []
        for ci in video.findall('./cl/ci'):
            clip_size = int(ci.find('./cs').text)
            clip_idx = int(ci.find('./idx').text)
            clips.append({'idx': clip_idx, 'size': clip_size})

        size = 0
        for clip in clips:
            size += clip['size']

        fns = os.path.splitext(filename)

        #may have preformence issue when info_only

        urls =[]
        for clip in clips:
            fn = '%s.%d%s' % (fns[0], clip['idx'], fns[1])
            params = {
                'vid': self.vid,
                'otype': 'xml',
                'platform': PLAYER_PLATFORM,
                'format': fmt_id,
                'charge': 0,
                'ran': random.random(),
                'filename': fn,
                'vt': vt,
                'appver': PLAYER_VERSION,
                'cKey': load_key(),
                'encryptVer': KLIB_VERSION
            }

            form = urllib.parse.urlencode(params)
            key_url = '%s?%s' % ('http://vv.video.qq.com/getvkey', form)
            content = get_content(key_url)
            tree = ET.fromstring(content)

            vkey = tree.find('./key').text
            level = tree.find('./level').text
            sp = tree.find('./sp').text

            clip_url = '%s%s' % (cdn_url, fn)

            urls.append(qq_get_final_url(clip_url, fmt_name, type_name, fmt_br, sp, vkey, level))

        return fmt_name, type_name, urls, size

    def prepare(self, **kwargs):
        assert self.url or self.vid

        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, 'vid:\"([^\"]+)')

        assert self.vid

        fmt_name, type_name, urls, size = self.get_stream_info(self.supported_stream_types[0])

        self.stream_types = self.supported_stream_types[self.supported_stream_types.index(fmt_name):]

        self.streams[fmt_name] = {'container': type_name, 'video_profile': self.stream_2_profile[fmt_name], 'src' : urls, 'size': size}

        if 'info_only' in kwargs and kwargs['info_only']:
            for stream in self.stream_types[1:]:
                fmt_name, type_name, urls, size = self.get_stream_info(stream)
                self.streams[fmt_name] = {'container': type_name, 'video_profile': self.stream_2_profile[fmt_name], 'src' : urls, 'size': size}


site = QQ()
download = site.download_by_url
download_playlist = playlist_not_supported('qq')
