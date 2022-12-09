# -*- coding: utf-8 -*-

from ._common import *


class JustFunLive(Extractor):
    name = '抓饭直播 (JustFun Live)'

    def prepare_mid(self):
        return match1(self.url, 'live/(\d+)')

    def prepare(self):
        info = MediaInfo(self.name, True)

        try:
            data = get_response(
                    'https://www.zhuafan.tech/live-channel-info/channel/v2/info',
                    params={
                        'cid': self.mid,
                        'decrypt': 1
                    }).json()
        except:
            html = get_content(self.url)
            data = match1(html, 'window\.__INITIAL_STATE__ = ({.+})</script>')
            self.logger.debug('data:\n%s', data)
            data = json.loads(data)['channel']

        assert data['playStatusCode'] == 0, data['playStatusCodeDesc']

        info.artist = data['uname']
        info.title = data['cname']

        info.streams['OG-FLV'] = {
            'container': 'flv',
            'profile': 'current',
            'src' : [data['httpsPlayInfo']],
            'size': Infinity
        }
        info.streams['OG-HLS'] = {
            'container': 'm3u8',
            'profile': 'current',
            'src' : [data['hlsPlayInfo']],
            'size': Infinity
        }

        return info

site = JustFunLive()
