#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import add_default_handler, install_default_handlers, get_content, add_header
from ykdl.util.match import match1, matchall
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.compact import HTTPCookieProcessor

import json
import sys
import base64
import uuid
import time


encode_translation = bytes.maketrans(b'+/=', b'_~-')
decode_translation = bytes.maketrans(b'_~-', b'+/=')

def encode_tk2(s):
    if not isinstance(s, bytes):
        s = s.encode()
    s = bytearray(base64.b64encode(s).translate(encode_translation))
    s.reverse()
    return s.decode()

def decode_tk2(s):
    if not isinstance(s, bytes):
        s = s.encode()
    s = bytearray(s)
    s.reverse()
    s = base64.b64decode(s.translate(decode_translation))
    return s.decode()

def generate_tk2(did):
    s = 'did={}|pno=1030|ver=0.3.0301|clit={}'.format(did, int(time.time()))
    return encode_tk2(s)

class Hunantv(VideoExtractor):
    name = '芒果TV (HunanTV)'

    supported_stream_types = [ 'BD', 'TD', 'HD', 'SD' ]
    profile_2_types = {
        '复刻版': 'BD',
        '蓝光': 'BD',
        '超清': 'TD',
        '高清': 'HD',
        '标清': 'SD'
    }

    def prepare(self):
        add_default_handler(HTTPCookieProcessor)
        install_default_handlers()
        add_header('Referer', self.url)

        info = VideoInfo(self.name)
        if self.url and not self.vid:
            self.vid = match1(self.url, 'com/[bl]/\d+/(\d+).html')
            if self.vid is None:
                self.vid = match1(self.url, 'com/s/(\d+).html')
            if self.vid is None:
                html = get_content(self.url)
                if match1(self.url, 'com/h/(\d+).html'):
                    from ykdl.util.jsengine import JSEngine
                    assert JSEngine, 'No JS Interpreter found!!!'
                    js_ctx = JSEngine()
                    js = match1(html, '<script>window.__NUXT__=(.+);</script>')
                    data = str(js_ctx.eval(js))
                    self.vid = match1(data, "PartId': '(\d+)'")
                else:
                    self.vid = match1(html, 'window.location = "/b/\d+/(\d+).html"',
                                           r'routePath:"\\u002Fl\\u002F\d+\\u002F(\d+).html"',
                                            'vid[=:]\D?(\d+)')
        assert self.vid, 'can not find video!!!'

        did = str(uuid.uuid4())
        tk2 = generate_tk2(did)

        api_info_url = 'https://pcweb.api.mgtv.com/player/video?tk2={}&video_id={}&type=pch5'.format(tk2, self.vid)
        meta = json.loads(get_content(api_info_url))
        self.logger.debug('meta >\n%s', meta)

        assert meta['code'] == 200, '[failed] code: {}, msg: {}'.format(meta['code'], meta['msg'])
        assert meta['data'], '[Failed] Video info not found.'

        pm2 = meta['data']['atc']['pm2']
        info.title = meta['data']['info']['title'] + ' ' + meta['data']['info']['desc']

        api_source_url = 'https://pcweb.api.mgtv.com/player/getSource?pm2={}&tk2={}&video_id={}&type=pch5'.format(pm2, tk2, self.vid)
        meta = json.loads(get_content(api_source_url))

        assert meta['code'] == 200, '[failed] code: {}, msg: {}'.format(meta['code'], meta['msg'])
        assert meta['data'], '[Failed] Video source not found.'

        data = meta['data']
        domain = data['stream_domain'][0]
        for lstream in data['stream']:
            lurl = lstream['url']
            if lurl:
                lurl = '{}{}&did={}'.format(domain, lurl, did)
                url = json.loads(get_content(lurl))['info']
                video_profile = lstream['name']
                stream = self.profile_2_types[video_profile]
                info.streams[stream] = {
                    'container': 'm3u8',
                    'video_profile': video_profile,
                    'src' : [url]
                }
                info.stream_types.append(stream)
        info.stream_types= sorted(info.stream_types, key = self.supported_stream_types.index)
        info.extra['referer'] = self.url
        return info

site = Hunantv()
