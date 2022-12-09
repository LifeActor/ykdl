# -*- coding: utf-8 -*-

from ._common import *


encode_translation = bytes.maketrans(b'+/=', b'_~-')
decode_translation = bytes.maketrans(b'_~-', b'+/=')

def encode_tk2(s):
    s = bytearray(base64.b64encode(s.encode()).translate(encode_translation))
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

class Hunantv(Extractor):
    name = '芒果TV (HunanTV)'

    profile_2_id = {
      '复刻版': 'BD',
        '蓝光': 'BD',
        '超清': 'TD',
        '高清': 'HD',
        '标清': 'SD'
    }

    def prepare_mid(self):
        mid = match1(self.url, 'com/[bl]/\d+/(\d+).html',
                               'com/s/(\d+).html')
        if mid is None:
            html = get_content(self.url)
            if match1(self.url, 'com/h/(\d+).html'):
                assert JSEngine, 'No JS Interpreter found!!!'
                js_ctx = JSEngine()
                js = match1(html, '<script>window.__NUXT__=(.+);</script>')
                data = js_ctx.eval(js)
                mid = match1(data, "PartId': '(\d+)'")
            else:
                mid = match1(html,
                             'window.location = "/b/\d+/(\d+).html"',
                            r'routePath:"\\u002Fl\\u002F\d+\\u002F(\d+).html"',
                             'vid[=:]\D?(\d+)')
        return mid

    def prepare(self):
        info = MediaInfo(self.name)
        info.extra.referer = self.url
        install_cookie()

        did = get_random_uuid()
        tk2 = generate_tk2(did)
        params = {
            'tk2': tk2,
            'video_id': self.mid,
            'type': 'pch5'
        }
        data = get_response('https://pcweb.api.mgtv.com/player/video',
                            params=params).json()
        assert data['code'] == 200, ('[failed] code: {}, msg: {}'
                                     .format(data['code'], data['msg']))
        assert data['data'], '[Failed] Video info not found.'
        data = data['data']

        info.title = data['info']['title'] + ' ' + data['info']['desc']

        params['pm2'] = data['atc']['pm2']
        data = get_response('https://pcweb.api.mgtv.com/player/getSource',
                            params=params).json()
        assert data['code'] == 200, ('[failed] code: {}, msg: {}'
                                     .format(data['code'], data['msg']))
        assert data['data'], '[Failed] Video source not found.'
        data = data['data']

        domain = data['stream_domain'][0]
        for lstream in data['stream']:
            lurl = lstream['url']
            if lurl:
                url = get_response(domain + lurl,
                                   params={'did': did}).json()['info']
                stream_profile = lstream['name']
                stream_id = self.profile_2_id[stream_profile]
                info.streams[stream_id] = {
                    'container': 'm3u8',
                    'profile': stream_profile,
                    'src': [url]
                }

        return info

site = Hunantv()
