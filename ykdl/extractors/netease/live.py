#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo

import time
import json

class NeteaseLive(VideoExtractor):
    name = u"网易直播 (163)"

    def prepare(self):
        info = VideoInfo(self.name, True)

        if self.vid is None:
            self.vid = match1(self.url, 'room/(\d+)')

        tt = int(time.time() * 1000)
        url = 'https://data.live.126.net/liveAll/{}.json?{}'.format(self.vid, tt)
        data = json.loads(get_content(url))
        self.logger.debug('video_data: \n%s', data)
        assert 'liveVideoUrl' in data, 'live video is offline'

        info.title = data['roomName']
        try:
            info.artist = data['sourceinfo']['tname']
        except KeyError:
            pass

        url = data['liveVideoUrl']
        info.stream_types.append('current')
        info.streams['current'] = {
            'container': url.split('.')[-1],
            'video_profile': 'current',
            'src': [url],
            'size': 0
        }
        return info

site = NeteaseLive()
