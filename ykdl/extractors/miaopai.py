# -*- coding: utf-8 -*-

from ._common import *


# BROKEN

api_info1 = 'https://n.miaopai.com/api/aj_media/info.json?smid={}&appid=530&_cb={}'
api_info2 = 'http://api.miaopai.com/m/v2_channel.json?fillType=259&scid={}&vend='
api_stream = 'http://gslb.miaopai.com/stream/{}.json?vend='

class Miaopai(Extractor):

    name = '秒拍 (Miaopai)'

    def prepare_mid(self):
        mid = match1(self.url, '/media/([^\./]+)')
        if mid is None:
            html = get_content(self.url)
            mid = match1(html, 's[cm]id ?= ?[\'"]([^\'"]+)[\'"]')
        return mid

    def prepare(self):
        info = MediaInfo(self.name)
        title = None

        if 'show' in self.url:
            new_url = get_location(self.url)
            if new_url != self.url:
                self.logger.debug('redirect to' + new_url)
                self.url = new_url

        if len(self.mid) > 24:
            add_header('Referer', self.url)
            cb = '_jsonp{}'.format(get_random_str(10).lower())
            data = get_response(api_info1.format(self.mid, cb)).json()
            data = json.loads(json_html[json_html.find('{'):-2])
            assert data['code'] == 200, data['msg']

            data = data['data']
            title = data['description']
            url = data['meta_data'][0]['play_urls']['m']
            _, ext, _ = url_info(url)
        
        else:
            try:
                data = get_response(api_info2.format(self.mid)).json()
                assert data['status'] == 200, data['msg']

                data = data['result']
                title = data['ext']['t']
                scid = data['scid'] or self.mid
                ext = data['stream']['and']
                base = data['stream']['base']
                vend = data['stream']['vend']
                url = '{base}{scid}.{ext}?vend={vend}'.format(**vars())
            except:
                # fallback
                data = get_response(api_stream.format(self.mid)).json()
                assert data['status'] == 200, data['msg']

                data = data['result'][0]
                ext = None
                scheme = data['scheme']
                host = data['host']
                path = data['path']
                sign = data['sign']
                url = '{scheme}{host}{path}{sign}'.format(**vars())

        if not title:
            html = get_content(self.url)
            title = match1(html, '<meta name="description" content="([^"]+)">')
        info.title = title

        info.streams['current'] = {
            'container': ext or 'mp4',
            'profile': 'current',
            'src': [url]
        }
        return info

    def prepare_list(self):
        html = get_content(self.url)
        video_list = match1(html, 'video_list=\[([^\]]+)')
        return matchall(video_list, '"([^",]+)')

site = Miaopai()
