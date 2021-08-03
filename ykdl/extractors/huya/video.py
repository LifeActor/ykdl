#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.util.html import get_content
from ykdl.util.match import match1

import json
import time
import random

from urllib.parse import urlencode


class HuyaVideo(VideoExtractor):
    name = 'huya video (虎牙视频)'

    supported_stream_types = ['BD', 'TD', 'HD', 'SD']
    quality_2_id_profile = {
        'yuanhua': ['BD', '原画'],
           '1300': ['TD', '超清'],
          #'TODO': ['HD', '高清'],
            '350': ['SD', '流畅']
    }

    def prepare(self):
        info = VideoInfo(self.name)

        self.vid = match1(self.url, 'play/(\d+)')
        html = get_content(self.url)
        if not self.vid:
            self.vid = match1(html, 'data-vid="(\d+)')
        title = match1(html, '<h1 class="video-title">(.+?)</h1>')
        info.artist = artist = match1(html, "<div class='video-author'>[\s\S]+?<h3>(.+?)</h3>")
        info.title = u'{} - {}'.format(title, artist)

        t1 = int(time.time() * 1000)
        t2 = t1 + random.randrange(5, 10)
        rnd = str(random.random()).replace('.', '')
        params = {
            'callback': 'jQuery1124{}_{}'.format(rnd, t1),
            'r': 'vhuyaplay/video',
            'vid': self.vid,
            'format': 'mp4,m3u8',
            '_': t2
        }
        api_url = 'https://v-api-player-ssl.huya.com/?' + urlencode(params)
        data = get_content(api_url)[len(params['callback']) + 1:-1]
        self.logger.debug('data:\n%s', data)
        
        data = json.loads(data)
        assert data['code'] == 1, data['message']
        data = data['result']['items']

        for stream_date in data:
            ext = stream_date['format']
            quality =stream_date['definition']
            stream, video_profile = self.quality_2_id_profile[quality]
            if stream not in info.stream_types:
                info.stream_types.append(stream)
            elif ext == 'm3u8':
                # prefer mp4
                continue
            url = stream_date['transcode']['urls'][0]
            info.streams[stream] = {
                'container': ext,
                'video_profile': video_profile,
                'src': [url],
                'size' : int(stream_date['size'])
            }

        info.stream_types = sorted(info.stream_types, key = self.supported_stream_types.index)
        return info

site = HuyaVideo()
