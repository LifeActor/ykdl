# -*- coding: utf-8 -*-

from .._common import *


class HuyaVideo(Extractor):
    name = 'huya video (虎牙视频)'

    quality_2_id_profile = {
        'yuanhua': ['BD', '原画'],
           '1300': ['TD', '超清'],
          #'TODO': ['HD', '高清'],
            '350': ['SD', '流畅']
    }

    def prepare_mid(self):
        mid = match1(self.url, 'play/(\d+)')
        if mid is None:
            html = get_content(self.url)
            mid = match1(html, 'vid = (\d+)', 'data-vid="(\d+)')
        return mid

    def prepare(self):
        info = MediaInfo(self.name)

        html = get_content(self.url)
        info.title = match1(html, '<h1 class="video-title">(.+?)</h1>')
        info.artist = match1(html, '<div class="video-author">[\s\S]+?<h3>(.+?)</h3>')

        t1 = int(time.time() * 1000)
        t2 = t1 + random.randrange(5, 10)
        rnd = str(random.random()).replace('.', '')
        data = get_response('https://v-api-player-ssl.huya.com/',
                        params={
                            'callback': 'jQuery1124{rnd}_{t1}'.format(**vars()),
                            'r': 'vhuyaplay/video',
                            'vid': self.mid,
                            'format': 'mp4,m3u8',
                            '_': t2
                        }).json()
        assert data['code'] == 1, data['message']
        data = data['result']['items']

        for stream_date in data:
            ext = stream_date['format']
            quality =stream_date['definition']
            stream_id, stream_profile = self.quality_2_id_profile[quality]
            stream_id += '-' + ext
            url = stream_date['transcode']['urls'][0]
            info.streams[stream_id] = {
                'container': ext,
                'profile': stream_profile,
                'src' : [url],
                'size': int(stream_date['size'])
            }

        return info

site = HuyaVideo()
