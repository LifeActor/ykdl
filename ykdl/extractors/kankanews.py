# -*- coding: utf-8 -*-

from ._common import *


# TODO: Live & TV

class KankanNews(Extractor):
    name = '看看新闻 (kankannews)'

    def prepare(self):
        info = MediaInfo(self.name)

        html = get_content(self.url)
        vid = match1(html, 'omsid="(\d+)"')
        assert vid, 'No omsid has been found!!'

        info.artist = match1(html, 'keyboard:"(.+?)"')
        info.title = info.artist + \
                     match1(html, '<title>视频(.+?)_[^_]+_看看新闻</title>')

        params = [
            ('nonce', get_random_str(8).lower()),
            ('omsid', vid),
            ('platform', 'pc'),
            ('timestamp', int(time.time())),
            ('version', '1.0')
        ]
        sign = hash.md5(hash.md5(urlencode(params) +
                                 '&28c8edde3d61a0411511d3b1866f0636'))
        params.append(('sign', sign))
        data = get_response('https://api-app.kankanews.com/kankan/pc/getvideo',
                            params=params).json()
        assert data['code'] == '10000', data['error']['message']
        data = data['result']['video']

        info.streams['current'] = {
            'container': 'mp4',
            'profile': 'current',
            'src' : [data['videourl']],
            'size': int(data['filesize'])
        }
        return info

site = KankanNews()
