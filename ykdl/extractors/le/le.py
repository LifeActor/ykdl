# -*- coding: utf-8 -*-

from .._common import *


def calcTimeKey(t):
    ror = lambda val, r_bits: ((val & (2**32-1)) >> r_bits%32) | \
                              (val << (32-(r_bits%32)) & (2**32-1))
    magic = 185025305
    return ror(t, magic % 17) ^ magic

def decode(data):
    version = data[0:5]
    if version.lower() == b'vc_01':
        #get real m3u8
        loc2 = bytearray(data[5:])
        length = len(loc2)
        loc4 = [0]*(2*length)
        for i in range(length):
            loc4[2*i] = loc2[i] >> 4
            loc4[2*i+1]= loc2[i] & 15;
        loc6 = loc4[len(loc4)-11:]+loc4[:len(loc4)-11]
        loc7 = bytearray(length)
        for i in range(length):
            loc7[i] = (loc6[2 * i] << 4) +loc6[2*i+1]
        return loc7
    else:
        # directly return
        return data

class Letv(Extractor):
    name = '乐视 (Letv)'

    stream_2_id_profile = {
        '1080p': ['BD', '1080P'],
         '1300': ['TD', '超清'],
         '1000': ['HD', '高清'],
         '720p': ['SD', '标清'],
          '350': ['LD', '流畅']
    }

    __STREAM_TEMP__ = []


    def prepare(self):
        info = MediaInfo(self.name)
        stream_temp = {st: None for st in self.stream_2_id_profile.keys()}
        self.__STREAM_TEMP__.append(stream_temp)
        if not self.vid:
            self.vid = match1(self.url, 'vplay/(\d+).html', '#record/(\d+)')

        #normal process
        data = get_response('http://player-pc.le.com/mms/out/video/playJson',
                            params={
                                'id': self.vid,
                                'platid': 1,
                                'splatid': 105,
                                'format': 1,
                                'tkey': calcTimeKey(int(time.time())),
                                'domain': 'www.le.com',
                                'region': 'cn',
                                'source': 1000,
                                'accessyx': 1
                            }).json()['msgs']

        info.title = data['playurl']['title']
        for stream, sdp in data['playurl']['dispatch'].items():
            s_url = data['playurl']['domain'][0] + sdp[0]
            data2 = get_response(s_url, params={
                                            'm3v': 1,
                                            'termid': 1,
                                            'format': 1,
                                            'hwtype': 'un',
                                            'ostype': 'MacOS10.12.4',
                                            'p1': 1,
                                            'p2': 10,
                                            'p3': '-',
                                            'expect': '3',
                                            'tn': random.random(),
                                            'vid': self.vid,
                                            'uuid': hash.sha1(s_url) + '_0',
                                            'tss': 'ios'
                                        }).json()

            # hold on ! more things to do
            # to decode m3u8 (encoded)
            m3u8 = get_content(data2['location'],
                               params={
                                   'r': int(time.time() * 1000),
                                   'appid': 500
                               },
                               encoding='ignore')
            m3u8_list = decode(m3u8)
            stream_id, video_profile = self.stream_2_id_profile[stream]
            info.streams[stream_id] = {
                'container': 'm3u8',
                'video_profile': video_profile,
                'size' : 0
            }
            stream_temp[stream] = NamedTemporaryFile(mode='w+b', suffix='.m3u8')
            stream_temp[stream].write(m3u8_list)
            info.streams[stream_id]['src'] = [stream_temp[stream].name]
            stream_temp[stream].flush()

        return info

    def prepare_list(self):
        html = get_content(self.url)
        return matchall(html, 'vid="(\d+)"')

site = Letv()
