# -*- coding: utf-8 -*-

from ._common import *


class Baomihua(Extractor):
    # https://www.baomihua.com/
    name = '爆米花（Baomihua)'

    def prepare_mid(self):
        return match1(self.url, '_(\d+)', 'm/(\d+)', 'v/(\d+)')

    def prepare(self):
        info = MediaInfo(self.name)

        add_header('Referer', 'https://m.mideo.baomihua.com/')
        data = get_response('https://play.baomihua.com/getvideourl.aspx',
                            params={
                                'flvid': self.mid,
                                'datatype': 'json',
                                'devicetype': 'wap'
                            }).json()

        info.title = data['title']
        host = data['host']
        stream_name = data['stream_name']
        t = data['videofiletype']
        size = int(data['videofilesize'])

        hls = data['ishls']
        url = 'http://{host}/{hls}/{stream_name}.{t}'.format(**vars())
        info.streams['current'] = {
            'container': t,
            'profile': 'current',
            'src' : [url],
            'size': size
        }
        return info

site = Baomihua()
