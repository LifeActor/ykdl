#!/usr/bin/env python

import json
import random
import base64, time, re

from ..common import *
from ..extractor import VideoExtractor

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
            loc4[2*i] = loc2[i] >> 4
            loc4[2*i+1]= loc2[i] & 15;
        loc6 = loc4[len(loc4)-11:]+loc4[:len(loc4)-11]
        loc7 = [0]*length
        for i in range(length):
            loc7[i] = (loc6[2 * i] << 4) +loc6[2*i+1]
        return ''.join([chr(i) for i in loc7])
    else:
        # directly return
        return data

class Letv(VideoExtractor):
    name = "乐视 (Letv)"

    supported_stream_types = [ '1080p', '1300', '1000', '720p', '350' ]


    def prepare(self, **kwargs):
        assert self.url or self.vid

        if self.vid:
            self.url = "http://www.letv.com/ptv/vplay/{}.html".format(self.vid)
        html = get_content(self.url)
        if not self.vid:
            self.vid = match1(self.url, r'http://www.letv.com/ptv/vplay/(\d+).html')
        if not self.vid:
           #self embed
           vids = matchall(html, ['vid="(\d+)"'])
           for v in vids:
               self.download_by_vid(v, **kwargs)

        #normal process
        self.title = match1(html,r'name="irTitle" content="(.*?)"')
        info_url = 'http://api.letv.com/mms/out/video/playJson?id={}&platid=1&splatid=101&format=1&tkey={}&domain=www.letv.com'.format(self.vid, calcTimeKey(int(time.time())))
        r = get_content(info_url)
        info=json.loads(r)
        available_stream_id = info["playurl"]["dispatch"].keys()
        for stream in self.supported_stream_types:
            if stream in available_stream_id:
                s_url =info["playurl"]["domain"][0]+info["playurl"]["dispatch"][stream][0]
                ext = info["playurl"]["dispatch"][stream][1].split('.')[-1]
                s_url+="&ctv=pc&m3v=1&termid=1&format=1&hwtype=un&ostype=Linux&tag=letv&sign=letv&expect=3&tn={}&pay=0&iscpn=f9051&rateid={}".format(random.random(),stream)
                r2=get_content(s_url)
                info2=json.loads(r2)

                # hold on ! more things to do
                # to decode m3u8 (encoded)
                m3u8 = get_content(info2["location"])
                m3u8_list = decode(m3u8)
                self.streams[stream] = {'container': ext, 'video_profile': stream, 'size' : 0}
                if self.param.player:
                    import tempfile
                    self.streams[stream]['tmp'] = tempfile.NamedTemporaryFile(mode='w+t', suffix='.m3u8')
                    self.streams[stream]['tmp'].write(m3u8_list)
                    self.streams[stream]['src'] = [self.streams[stream]['tmp'].name]
                else:
                    urls = re.findall(r'^[^#][^\r]*',m3u8_list,re.MULTILINE)
                    self.streams[stream]['src'] = urls
                self.stream_types.append(stream)

    def extract(self, **kwargs):
        if self.param.info_only:
            for stream_id in self.streams.keys():
                size = 0
                for i in self.streams[stream_id]['src']:
                    _, _, tmp = url_info(i)
                    size += tmp
                self.streams[stream_id]['size'] = size
        return
        #ignore video size in download/play mode, for preformence issue
        stream_id = self.param.stream_id or self.stream_type[0]

        size = 0
        for i in self.streams[stream_id]['src']:
             _, _, tmp = url_info(i)
             size += tmp
             self.streams[stream_id]['size'] = size

    def download_playlist_by_url(self, url, param, **kwargs):
        self.url = url
        self.param = param
        html = get_content(self.url)

        vids = matchall(html, ['vid="(\d+)"'])
        for v in vids:
            self.download_by_vid(v,param, **kwargs)


def letvcloud_download_by_vu(vu, uu, title=None, output_dir='.', merge=True, info_only=False, **kwargs):
    from .letvcloud import letvcloud_download_by_vid
    letvcloud_download_by_vid((vu, uu), title=title, output_dir=output_dir, merge=merge, info_only=info_only,**kwargs)

site = Letv()
download = site.download_by_url
letv_download_by_vid = site.download_by_vid
download_playlist = site.download_playlist_by_url
