#!/usr/bin/env python3

from ..extractor import VideoExtractor
from ..util.html import get_content
from ..util.match import match1
from ..util import log

import json

class YinYueTai(VideoExtractor):
    name = 'YinYueTai (音乐台)'
    supported_stream_types = ['he', 'hd', 'hc' ]
    def prepare(self):
        assert self.url or self.vid

        if not self.vid:
            self.vid = match1(self.url, 'http://\w+.yinyuetai.com/video/(\d+)')

        data = json.loads(get_content('http://ext.yinyuetai.com/main/get-h-mv-info?json=true&videoId={}'.format(self.vid)))

        if data['error']:
            log.e('some error happens')

        video_data = data['videoInfo']['coreVideoInfo']

        self.title = video_data['videoName']

        for s in video_data['videoUrlModels']:
            self.stream_types.append(s['qualityLevel'])
            self.streams[s['qualityLevel']] = {'container': 'flv', 'video_profile': s['qualityLevelName'], 'src' : [s['videoUrl']], 'size': s['fileSize']}

        self.stream_types = sorted(self.stream_types, key = self.supported_stream_types.index)

site = YinYueTai()
