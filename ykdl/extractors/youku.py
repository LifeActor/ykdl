# -*- coding: utf-8 -*-

from ._common import *
from .youkujs import stream_code_to_id, stream_code_to_profiles, id_to_container

import struct
import hmac
import hashlib
from ctypes import c_int


def hashCode(str):
    res = c_int(0)
    if not isinstance(str, bytes):
        str = str.encode()
    for i in bytearray(str):
        res = c_int(c_int(res.value * 0x1f).value + i)
    return res.value

def generateUtdid():
    timestamp = int(time.time()) - 60 * 60 * 8
    i31 = random.randrange(1 << 31)
    imei = hashCode(str(i31))
    msg = struct.pack('!2i2bi', timestamp, i31, 3, 0, imei)
    key = b'd6fc3a4a06adbde89223bvefedc24fecde188aaa9161'
    data = hmac.new(key, msg, hashlib.sha1).digest()
    msg += struct.pack('!i', hashCode(base64.standard_b64encode(data)))
    return base64.standard_b64encode(msg)

class Youku(Extractor):
    name = '优酷 (Youku)'
    ref_youku = 'https://v.youku.com'
    ref_tudou = 'https://video.tudou.com'
    ckey_default = 'DIl58SLFxFNndSV1GFNnMQVYkx1PP5tKe1siZu/86PR1u/Wh1Ptd+WOZsHHWxysSfAOhNJpdVWsdVJNsfJ8Sxd8WKVvNfAS8aS8fAOzYARzPyPc3JvtnPHjTdKfESTdnuTW6ZPvk2pNDh4uFzotgdMEFkzQ5wZVXl2Pf1/Y6hLK0OnCNxBj3+nb0v72gZ6b0td+WOZsHHWxysSo/0y9D2K42SaB8Y/+aD2K42SaB8Y/+ahU+WOZsHcrxysooUeND'
    ckey_mobile = '7B19C0AB12633B22E7FE81271162026020570708D6CC189E4924503C49D243A0DE6CD84A766832C2C99898FC5ED31F3709BB3CDD82C96492E721BDD381735026'
    params = (
        ('0532', ref_youku, ckey_default),
        ('0590', ref_youku, ckey_default),
        ('0505', ref_tudou, ckey_default),
        )

    def prepare_mid(self):
        mid = match1(self.url.split('//', 1)[1],
                    '^v[^\.]?\.[^/]+/v_show/id_([a-zA-Z0-9=]+)',
                    '^player[^/]+/(?:player\.php/sid|embed)/([a-zA-Z0-9=]+)',
                    '^static.+loader\.swf\?VideoIDS=([a-zA-Z0-9=]+)',
                    '^(?:new-play|video)\.tudou\.com/v/([a-zA-Z0-9=]+)')
        if mid is None:
            html = get_content(self.url)
            mid = match1(html, '''videoIds?["']?\s*[:=]\s*["']?([a-zA-Z0-9=]+)''')
        elif mid.isdigit():
            mid = 'X' + b64('%d' % (int(mid) * 4))
        return mid

    def prepare(self):
        info = MediaInfo(self.name)

        install_cookie()
        get_response('https://gm.mmstat.com/yt/ykcomment.play.commentInit?cna=',
                     {'Cookie': '__ysuid=%d' % time.time()})
        utid = get_cookie('.mmstat.com', '/', 'cna').value
        uninstall_cookie()

        for ccode, ref, ckey in self.params:
            add_header('Referer', ref)
            if len(ccode) > 4:
               _utid = generateUtdid()
            else:
               _utid = utid
            params = {
                'vid': self.mid,
                'ccode': ccode,
                'utid': _utid,
                'ckey': ckey,
                'client_ip': '192.168.1.1',
                'client_ts': int(time.time()),
            }
            data = None
            while data is None:
                e1 = 0
                e2 = 0
                data = get_response('https://ups.youku.com/ups/get.json',
                                    params=params).json()
                e1 = data['e']['code']
                e2 = data['data'].get('error')
                if e2:
                    e2 = e2['code']
                if e1 == 0 and e2 in (-2002, -2003):
                    from getpass import getpass
                    data = None
                    if e2 == -2002:
                        self.logger.warning('This video has protected!')
                    elif e2 == -2003:
                        self.logger.warning('Your password [{}] is wrong!'.format(params['password']))
                    params['password'] = getpass('Input password:')
            if e1 == 0 and not e2:
                break

        assert e1 == 0, data['e']['desc']
        data = data['data']
        assert 'stream' in data, data['error']['note']

        try:
            # stage > 0，日期或集数等作为放映顺序，如 https://v.youku.com/v_show/id_XNDEyNDExMDIyNA==.html
            # stage == 0，未提供有意义的信息，如 https://v.youku.com/v_show/id_XNDU1MDMyMDI1Ng==.html
            stage = data['show']['stage'] or ''
        except KeyError:
            # 未提供相关信息，如 https://v.youku.com/v_show/id_XOTI0MTE2NDg4.html
            stage = ''
        info.title = '{} {}'.format(stage, data['video']['title']).lstrip()

        audio_lang = 'default'
        if 'dvd' in data and 'audiolang' in data['dvd']:
            for l in data['dvd']['audiolang']:
                if l['vid'].startswith(self.mid):
                    audio_lang = l['langcode']
                    break

        streams = data['stream']
        for s in streams:
            if not audio_lang == s['audio_lang']:
                continue
            self.logger.debug('stream> ' + str(s))
            stream_id = stream_code_to_id[s['stream_type']]
            stream_profile = stream_code_to_profiles[stream_id]
            urls = []
            for u in s['segs']:
                self.logger.debug('seg> ' + str(u))
                if u['key'] != -1:
                    if 'cdn_url' in u:
                        urls.append(u['cdn_url'])
                else:
                    self.logger.warning('VIP video, ignore unavailable seg: {}'
                                        .format(s['segs'].index(u)))
            if len(urls) == 0:
                urls = [s['m3u8_url']]
                c = 'm3u8'
            else:
                c = id_to_container[stream_id]
            size = s['size']
            info.streams[stream_id] =  {
                    'container': c,
                    'profile': stream_profile,
                    'src' : urls,
                    'size': size
                }

        return info


site = Youku()
