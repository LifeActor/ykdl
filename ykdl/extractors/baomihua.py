# -*- coding: utf-8 -*-

from ._common import *


class Baomihua(VideoExtractor):

    name = '爆米花（Baomihua)'

    def prepare(self):

        info = VideoInfo(self.name)
        if self.url:
            self.vid = match1(self.url, '_(\d+)', 'm/(\d+)', 'v/(\d+)')

        add_header('Referer', 'http://m.video.baomihua.com/')
        data = get_response('http://play.baomihua.com/getvideourl.aspx',
                            params={
                                'flvid': self.vid,
                                'datatype': 'json',
                                'devicetype': 'wap'
                            }).json()

        info.title = unquote(data['title'])
        host = data['host']
        stream_name = data['stream_name']
        t = data['videofiletype']
        size = int(data['videofilesize'])

        hls = data['ishls']
        url = 'http://{host}/{hls}/{stream_name}.{t}'.format(**vars())
        info.stream_types.append('current')
        info.streams['current'] = {
            'video_profile': 'current',
            'container': t,
            'src': [url],
            'size' : size
        }
        return info

site = Baomihua()
