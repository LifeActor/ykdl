#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo

import json

class NeteaseVideo(VideoExtractor):
    name = u"网易视频 (163)"

    def prepare(self):
        info = VideoInfo(self.name)

        if self.vid is None:
            self.vid = match1(self.url, '(\w+)\.html')

        url = 'https://so.v.163.com/v6/video/videodetail.do?vid={}&adapter=1'.format(self.vid)
        data = json.loads(get_content(url))
        self.logger.debug('video_data: \n%s', data)
        assert data['code'] == 1, data['msg']

        data = data['data']
        info.title = data['title']
        info.artist = data.get('username')
        info.stream_types.append('current')
        info.streams['current'] = {
            'container': 'mp4',
            'video_profile': 'current',
            'src' : [data['url']],
            'size': 0
        }
        return info

site = NeteaseVideo()
