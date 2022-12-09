# -*- coding: utf-8 -*-

from ._common import *


assert JSEngine, "No JS Interpreter found, can't extract heibaizhibo!"

js_m = get_pkgdata_str(__name__, 'heibaizhibo.m.js',
                       'https://pichb2.huoxinglaike.com/nuxt/static/m.js')

class Heibai(Extractor):
    name = '黑白直播'

    def prepare(self):
        info = MediaInfo(self.name, True)

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
            data = get_response('https://www.heibaizhibo.com/api/index/live',
                                params={'id': vid}).json()
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

        info.title = '{title} - {artist}'.format(**vars())
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
            data_live = get_response(
                'https://sig.heibaizhibo.com/signal-front/live/matchLiveInfo?',
                params=params).json()
            msg = data_live['msg']
            assert '成功' in msg, msg
            data_live = data_live['data'][0]
            assert data_live['score'] >= 0, 'live video is offline!'
            url = js_ctx.call('vp', data_live['liveUrl'])
            stream_id = ql['defi'].upper()
            info.streams[stream_id] = {
                'container': 'flv',
                'profile': ql['name'],
                'src' : [url],
                'size': Infinity
            }
            break  # seems the same quality?

        return info

site = Heibai()
