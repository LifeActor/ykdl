#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import random
import base64, time
import sys

if sys.version_info[0] == 3:
    WR_ord = int
else:
    WR_ord = ord

from ykdl.util.html import get_content, url_info
from ykdl.util.match import match1, matchall
from ykdl.extractor import VideoExtractor

def calcTimeKey(t):
    ror = lambda val, r_bits, : ((val & (2**32-1)) >> r_bits%32) |  (val << (32-(r_bits%32)) & (2**32-1))
    return ror(ror(t,773625421%13)^773625421,773625421%17)

def decode(data):
    version = data[0:5]
    if version.lower() == b'vc_01':
        #get real m3u8
        loc2 = data[5:]
        length = len(loc2)
        loc4 = [0]*(2*length)
        for i in range(length):
            loc4[2*i] = WR_ord(loc2[i]) >> 4
            loc4[2*i+1]= WR_ord(loc2[i]) & 15;
        loc6 = loc4[len(loc4)-11:]+loc4[:len(loc4)-11]
        loc7 = [0]*length
        for i in range(length):
            loc7[i] = (loc6[2 * i] << 4) +loc6[2*i+1]
        return ''.join([chr(i) for i in loc7])
    else:
        # directly return
        return data

class Letv(VideoExtractor):
    name = u"乐视 (Letv)"

    supported_stream_types = [ '1080p', '1300', '1000', '720p', '350' ]


    def prepare(self):

        if not self.vid:
            self.vid = match1(self.url, r'http://www.le.com/ptv/vplay/(\d+).html', '#record/(\d+)')

        #normal process
        info_url = 'http://api.le.com/mms/out/video/playJson?id={}&platid=1&splatid=101&format=1&tkey={}&domain=www.le.com'.format(self.vid, calcTimeKey(int(time.time())))
        r = get_content(info_url)
        info=json.loads(r)

        self.title = info['playurl']['title']
        available_stream_id = info["playurl"]["dispatch"].keys()
        for stream in self.supported_stream_types:
            if stream in available_stream_id:
                s_url =info["playurl"]["domain"][0]+info["playurl"]["dispatch"][stream][0]
                s_url+="&ctv=pc&m3v=1&termid=1&format=1&hwtype=un&ostype=Linux&tag=le&sign=le&expect=3&tn={}&pay=0&iscpn=f9051&rateid={}".format(random.random(),stream)
                r2=get_content(s_url)
                info2=json.loads(r2)

                # hold on ! more things to do
                # to decode m3u8 (encoded)
                m3u8 = get_content(info2["location"], charset = 'ignore')
                m3u8_list = decode(m3u8)
                self.streams[stream] = {'container': 'm3u8', 'video_profile': stream, 'size' : 0}
                import tempfile
                self.streams[stream]['tmp'] = tempfile.NamedTemporaryFile(mode='w+t', suffix='.m3u8')
                self.streams[stream]['tmp'].write(m3u8_list)
                self.streams[stream]['src'] = [self.streams[stream]['tmp'].name]
                self.streams[stream]['tmp'].flush()
                self.stream_types.append(stream)

    def extract(self):
        if self.param.info:
            for stream_id in self.streams.keys():
                size = 0
                for i in self.streams[stream_id]['src']:
                    _, _, tmp = url_info(i)
                    size += tmp
                self.streams[stream_id]['size'] = size
        return
        #ignore video size in download/play mode, for preformence issue
        stream_id = self.param.format or self.stream_types[0]

        size = 0
        for i in self.streams[stream_id]['src']:
             _, _, tmp = url_info(i)
             size += tmp
             self.streams[stream_id]['size'] = size

    def prepare_list(self):

        html = get_content(self.url)

        return matchall(html, ['vid="(\d+)"'])

site = Letv()
