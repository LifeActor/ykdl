#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content, add_header
from ykdl.util.match import match1, matchall
from ykdl.util import log
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.compact import HTTPSHandler, build_opener, HTTPCookieProcessor, install_opener, urlopen, quote
from .youkujs import supported_stream_code, ids, stream_code_to_id, stream_code_to_profiles, id_to_container


import time
import json
import ssl

ckey = quote("DIl58SLFxFNndSV1GFNnMQVYkx1PP5tKe1siZu/86PR1u/Wh1Ptd+WOZsHHWxysSfAOhNJpdVWsdVJNsfJ8Sxd8WKVvNfAS8aS8fAOzYARzPyPc3JvtnPHjTdKfESTdnuTW6ZPvk2pNDh4uFzotgdMEFkzQ5wZVXl2Pf1/Y6hLK0OnCNxBj3+nb0v72gZ6b0td+WOZsHHWxysSo/0y9D2K42SaB8Y/+aD2K42SaB8Y/+ahU+WOZsHcrxysooUeND")


def fetch_cna():
    url = 'http://gm.mmstat.com/yt/ykcomment.play.commentInit?cna='
    req = urlopen(url)
    cookies = req.info()['Set-Cookie']
    cna = match1(cookies, "cna=([^;]+)")
    return cna if cna else "oqikEO1b7CECAbfBdNNf1PM1"

class Youku(VideoExtractor):
    name = u"优酷 (Youku)"

    def __init__(self):
        VideoExtractor.__init__(self)
        self.ccode = '0510', '0590'
        self.ref = 'http://v.youku.com'


    def prepare(self):
        add_header("Referer", self.ref)
        ssl_context = HTTPSHandler(
            context=ssl.SSLContext(ssl.PROTOCOL_TLSv1))
        cookie_handler = HTTPCookieProcessor()
        opener = build_opener(ssl_context, cookie_handler)
        opener.addheaders = [('Cookie','__ysuid=%d' % time.time())]
        install_opener(opener)

        info = VideoInfo(self.name)

        if self.url and not self.vid:
             self.vid = match1(self.url.split('//', 1)[1],
                               '^v\.[^/]+/v_show/id_([a-zA-Z0-9=]+)',
                               '^player[^/]+/(?:player\.php/sid|embed)/([a-zA-Z0-9=]+)',
                               '^static.+loader\.swf\?VideoIDS=([a-zA-Z0-9=]+)',
                               '^(?:new-play|video)\.tudou\.com/v/([a-zA-Z0-9=]+)')

        self.logger.debug("VID: " + self.vid)
        for ccode in self.ccode:
            api_url = 'https://ups.youku.com/ups/get.json?vid={}&ccode={}&client_ip=192.168.1.1&utid={}&client_ts={}&ckey={}'.format(self.vid, ccode, quote(fetch_cna()), int(time.time()),ckey)

            data = json.loads(get_content(api_url))
            self.logger.debug("data: " + str(data))
            if data['e']['code'] == 0 and 'stream' in data['data']:
                    break
        assert data['e']['code'] == 0, data['e']['desc']
        data = data['data']
        assert 'stream' in data, data['error']['note']
        info.title = data['video']['title']
        audio_lang = 'default'
        if 'dvd' in data and 'audiolang' in data['dvd']:
            for l in data['dvd']["audiolang"]:
                if l['vid'].startswith(self.vid):
                    audio_lang = l['langcode']
                    break
        streams = data['stream']
        for s in streams:
            if not audio_lang == s['audio_lang']:
                continue
            self.logger.debug("stream> " + str(s))
            t = stream_code_to_id[s['stream_type']]
            urls = []
            for u in s['segs']:
                self.logger.debug("seg> " + str(u))
                if u['key'] != -1:
                    if 'cdn_url' in u:
                        urls.append(u['cdn_url'])
                else:
                    self.logger.warning("VIP video, ignore unavailable seg: {}".format(s['segs'].index(u)))
            if len(urls) == 0:
                urls = [s['m3u8_url']]
                c = 'm3u8'
            else:
                c = id_to_container[t]
            size = s['size']
            info.stream_types.append(t)
            info.streams[t] =  {
                    'container': c,
                    'video_profile': stream_code_to_profiles[t],
                    'size': size,
                    'src' : urls
                }
        info.stream_types = sorted(info.stream_types, key = ids.index)
        tmp = []
        for t in info.stream_types:
            if not t in tmp:
                tmp.append(t)
        info.stream_types = tmp
        return info


site = Youku()
