# -*- coding: utf-8 -*-

from ._common import *


class Baomihua(Extractor):
    # https://www.baomihua.com/
    name = '爆米花（Baomihua)'

    def prepare(self):

        info = MediaInfo(self.name)
        if self.url:
            self.vid = match1(self.url, '_(\d+)', 'm/(\d+)', 'v/(\d+)')

        add_header('Referer', 'https://m.video.baomihua.com/')
        data = get_response('https://play.baomihua.com/getvideourl.aspx',
                            params={
                                'flvid': self.vid,
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
            'video_profile': 'current',
            'container': t,
            'src': [url],
            'size' : size
        }
        return info

site = Baomihua()
