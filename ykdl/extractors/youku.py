#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content, add_header
from ykdl.util.match import match1, matchall
from ykdl.util import log
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.compact import urlopen, urlencode
from .youkujs import supported_stream_code, ids, stream_code_to_id, stream_code_to_profiles, id_to_container


import time
import json
import ssl


def fetch_cna():
    url = 'https://gm.mmstat.com/yt/ykcomment.play.commentInit?cna='
    req = urlopen(url)
    cookies = req.info()['Set-Cookie']
    cna = match1(cookies, "cna=([^;]+)")
    return cna if cna else "oqikEO1b7CECAbfBdNNf1PM1"

class Youku(VideoExtractor):
    name = u"优酷 (Youku)"
    ref_youku = 'https://v.youku.com'
    ref_tudou = 'https://video.tudou.com'
    ckey_default = "DIl58SLFxFNndSV1GFNnMQVYkx1PP5tKe1siZu/86PR1u/Wh1Ptd+WOZsHHWxysSfAOhNJpdVWsdVJNsfJ8Sxd8WKVvNfAS8aS8fAOzYARzPyPc3JvtnPHjTdKfESTdnuTW6ZPvk2pNDh4uFzotgdMEFkzQ5wZVXl2Pf1/Y6hLK0OnCNxBj3+nb0v72gZ6b0td+WOZsHHWxysSo/0y9D2K42SaB8Y/+aD2K42SaB8Y/+ahU+WOZsHcrxysooUeND"
    ckey_mobile = "7B19C0AB12633B22E7FE81271162026020570708D6CC189E4924503C49D243A0DE6CD84A766832C2C99898FC5ED31F3709BB3CDD82C96492E721BDD381735026"

    def __init__(self):
        VideoExtractor.__init__(self)
        self.params = (
            ('0515', self.ref_youku, self.ckey_default),
            ('0516', self.ref_youku, self.ckey_default),
            ('0517', self.ref_youku, self.ckey_default),
            )

    def prepare(self):
        add_header("Cookie", '__ysuid=%d' % time.time())

        info = VideoInfo(self.name)

        if self.url and not self.vid:
             self.vid = match1(self.url.split('//', 1)[1],
                               '^v[^\.]?\.[^/]+/v_show/id_([a-zA-Z0-9=]+)',
                               '^player[^/]+/(?:player\.php/sid|embed)/([a-zA-Z0-9=]+)',
                               '^static.+loader\.swf\?VideoIDS=([a-zA-Z0-9=]+)',
                               '^(?:new-play|video)\.tudou\.com/v/([a-zA-Z0-9=]+)')

        if self.vid.isdigit():
            import base64
            vid = base64.b64encode(b'%d' % (int(self.vid) * 4))
            if not isinstance(vid, str):
                vid = vid.decode()
            self.vid = 'X' + vid
        self.logger.debug("VID: " + self.vid)

        utid = fetch_cna()
        for ccode, ref, ckey in self.params:
            add_header("Referer", ref)
            params = {
                'vid': self.vid,
                'ccode': ccode,
                'utid': utid,
                'ckey': ckey,
                'client_ip': '192.168.1.1',
                'client_ts': int(time.time()),
            }
            data = json.loads(get_content('https://ups.youku.com/ups/get.json?' + urlencode(params)))
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
