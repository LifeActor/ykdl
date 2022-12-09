# -*- coding: utf-8 -*-

from ._common import *


def calcTimeKey(t):
    ror = lambda val, r_bits: ((val & (2**32-1)) >> r_bits%32) | \
                              (val << (32-(r_bits%32)) & (2**32-1))
    magic = 185025305
    return ror(t, magic % 17) ^ magic

def decode_m3u8(data):
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

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) '
                  'AppleWebKit/603.1.30 (KHTML, like Gecko) '
                  'Version/10.1 Safari/603.1.30'
}

class Letv(Extractor):
    name = '乐视视频 (Letv)'

    stream_2_id_profile = {
        '1080p': ['BD', '1080P'],
         '1300': ['TD', '超清'],
         '1000': ['HD', '高清'],
         '720p': ['SD', '标清'],
          '350': ['LD', '流畅']
    }

    __STREAM_TEMP__ = []

    def prepare_mid(self):
        return match1(self.url, '/vplay/(\d+).html', '#record/(\d+)')

    def prepare(self):
        info = MediaInfo(self.name)
        stream_temp = {st: None for st in self.stream_2_id_profile.keys()}
        self.__STREAM_TEMP__.append(stream_temp)

        #normal process
        data = get_response('https://player-pc.le.com/mms/out/video/playJson',
                            params={
                                'id': self.mid,
                                'platid': 1,
                                'splatid': 105,
                                'format': 1,
                                'tkey': calcTimeKey(int(time.time())),
                                'domain': 'www.le.com',
                                'region': 'cn',
                                'source': 1000,
                                'accessyx': 1
                            },
                            headers=headers).json()['msgs']['playurl']

        info.title = data['title']
        info.duration = data['duration']
        for stream, sdp in data['dispatch'].items():
            s_url = data['domain'][0] + sdp[0]
            data2 = get_response(s_url,
                                 params={
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
                                     'vid': self.mid,
                                     'uuid': hash.sha1(s_url) + '_0',
                                     'tss': 'ios'
                                 },
                                 headers=headers).json()

            # hold on ! more things to do
            # to decode m3u8 (encoded)
            m3u8 = get_content(data2['location'],
                               params={
                                   'r': int(time.time() * 1000),
                                   'appid': 500
                               },
                               headers=headers, encoding=decode_m3u8)
            stream_id, stream_profile = self.stream_2_id_profile[stream]
            info.streams[stream_id] = {
                'container': 'm3u8',
                'profile': stream_profile
            }
            stream_temp[stream] = NamedTemporaryFile(mode='w+b', suffix='.m3u8')
            stream_temp[stream].write(m3u8)
            info.streams[stream_id]['src'] = [stream_temp[stream].name]
            stream_temp[stream].flush()

        return info

    def list_only(self):
        return bool(match1(self.url, '/tv/\d+.html'))

    def prepare_list(self):
        if self.list_only():
            mid = None
        else:
            mid = self.mid
            html = get_content(self.url)
            pid = match1(html, r'\bpid: ?(\d+)')
            if pid is None:
                 return
            self.url = 'https://www.le.com/tv/{pid}.html'.format(**vars())

        html = get_content(self.url)
        vids = matchall(html, '/vplay/(\d+).html"')
        mids = []
        for vid in vids:
            if vid in mids:
                continue
            mids.append(vid)
        self.set_index(mid, mids)
        return mids

site = Letv()
