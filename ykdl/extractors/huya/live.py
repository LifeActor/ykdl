#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.util.html import get_content
from ykdl.util.match import match1

import os
import json
import time
import base64
import random
import hashlib

from html import unescape
from urllib.parse import unquote, urlencode


def md5(s):
    return hashlib.md5(s.encode()).hexdigest()

class HuyaLive(VideoExtractor):
    name = 'Huya Live (虎牙直播)'

    def profile_2_id_rate(self, profile):
        if profile[-1] == 'M':
            return profile.replace('蓝光', 'BD'), int(profile[2:-1]) * 1000
        else:
            return {
                '蓝光': ('BD', 3000),
                '超清': ('TD', 2000),
                '高清': ('HD', 0),
                '流畅': ('SD', 0)
            }[profile]

    def prepare(self):
        info = VideoInfo(self.name, True)

        html  = get_content(self.url)

        json_stream = match1(html, '"stream": "([a-zA-Z0-9+=/]+)"')
        assert json_stream, 'live video is offline'
        data = json.loads(base64.b64decode(json_stream).decode())
        self.logger.debug('data:\n%s', data)
        assert data['status'] == 200, data['msg']

        room_info = data['data'][0]['gameLiveInfo']
        info.title = '{}「{} - {}」'.format(
            room_info['roomName'], room_info['nick'], room_info['introduction'])
        info.artist = room_info['nick']

        stream_info = random.choice(data['data'][0]['gameStreamInfoList'])
        sUrl = stream_info['sFlvUrl']
        sStreamName = stream_info['sStreamName']
        sUrlSuffix = stream_info['sFlvUrlSuffix']
        sAntiCode = unquote(unescape(stream_info['sFlvAntiCode']))
        sAntiCode = dict(p.split('=', 1) for p in sAntiCode.split('&') if p)
        
        sAntiCode['uid'] = uid = '0'
        sAntiCode['seqid'] = seqid = str(int(os.urandom(5).hex(), 16))
        sAntiCode['ver'] = '1'
        sAntiCode['t'] = t = '100'
        ss = md5('|'.join([seqid, sAntiCode['ctype'], t]))
        fm = base64.b64decode(sAntiCode['fm']).decode().split('_', 1)[0]

        def link_url(rate):
            if rate:
                streamname = '{}_{}'.format(sStreamName, rate)
            else:
                streamname = sStreamName
            sAntiCode['wsSecret'] = md5('_'.join([fm, uid, streamname, ss, sAntiCode['wsTime']]))
            return '{}/{}.{}?{}'.format(sUrl, streamname, sUrlSuffix, urlencode(sAntiCode))

        for si in data['vMultiStreamInfo']:
            video_profile = si['sDisplayName']
            stream, _rate = self.profile_2_id_rate(video_profile)
            rate = si['iBitRate'] or _rate
            info.stream_types.append(stream)
            info.streams[stream] = {
                'container': 'flv',
                'video_profile': video_profile,
                'src': [link_url(rate)],
                'size' : float('inf')
            }
        return info

site = HuyaLive()
