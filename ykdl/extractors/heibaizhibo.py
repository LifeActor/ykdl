#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.util.jsengine import JSEngine

assert JSEngine, "No JS Interpreter found, can't parse heibaizhibo!"

import json
import pkgutil
from urllib.parse import urlencode


try:
    # try load local .js file first
    js_m = pkgutil.get_data(__name__, 'heibaizhibo.m.js')
except IOError:
    js_m = get_content('https://pichb2.huoxinglaike.com/nuxt/static/m.js')

class Heibai(VideoExtractor):
    name = '黑白直播'

    stream_ids = ['HD', 'SD']

    def prepare(self):
        info = VideoInfo(self.name, True)

        js_ctx = JSEngine('if (!this.window) {window = {};}')
        js_ctx.append(js_m)

        vid = match1(self.url, '/live/.*?(\d+)')
        if vid is None:
            html = get_content(self.url)
            js_data = match1(html, 'window.__NUXT__=(.+?)</script>')
            data = js_ctx.eval(js_data)
            self.logger.debug('data:\n%s', data)
            data = data['data'][0]
            data = data.get('videoInfo', data)
        else:
            data = get_content('https://www.heibaizhibo.com/api/index/live?id=' + vid)
            self.logger.debug('data:\n%s', data)
            data = json.loads(data)
            msg = data['message']
            assert '成功' in msg, msg
            data = data['data']['detail']

        try:
            qllist = data['hd']
        except KeyError:
            # anchor
            qllist = data['hdlist']
            title = data['anchorInfo']['title']
            artist = data['anchorInfo']['nickname']
        else:
            title = '[{}] {}({})'.format(
                data['eventName'], data['homeName'], data['awayName'])
            assert data['playCode'], 'live video is offline!'
            data = data['playCode'][0]
            artist = data['gtvDesc'] or data['name']

        info.title = '{} - {}'.format(title, artist)
        info.artist = artist
        params = {
            'gtvId': data.get('gtvId'),
            'id': data.get('id', 0),
            'type': 3,
            'source': 2,
            'liveType': 3,  # 1: rtmp, 2: m3u8, 3: flv
        }
        if not params['gtvId']:
            del params['gtvId']

        for ql in qllist:
            params['defi'] = ql['defi']
            data_live = json.loads(get_content(
                'https://sig.heibaizhibo.com/signal-front/live/matchLiveInfo?' +
                urlencode(params)))
            self.logger.debug('data_live:\n%s', data_live)
            msg = data_live['msg']
            assert '成功' in msg, msg
            data_live = data_live['data'][0]
            assert data_live['score'] >= 0, 'live video is offline!'
            url = js_ctx.call('vp', data_live['liveUrl'])
            stream = ql['defi'].upper()
            info.stream_types.append(stream)
            info.streams[stream] = {
                'container': 'flv',
                'video_profile': ql['name'],
                'src' : [url],
                'size': float('inf')
            }
            break  # seems the same quality?

        info.stream_types = sorted(info.stream_types, key=self.stream_ids.index)
        return info

site = Heibai()
