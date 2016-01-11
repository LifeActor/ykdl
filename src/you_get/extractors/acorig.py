#!/usr/bin/env python

from ..extractor import VideoExtractor
from ..util.html import get_content, fake_headers
import json

acorg_headers = fake_headers
acorg_headers['deviceType'] = '1'

class Acorig(VideoExtractor):
    name = "AcFun 原创"

    supported_stream_types = ['原画', '超清', '高清', '标清']

    def prepare(self, **kwargs):
        assert self.url or self.vid

        if 'title' in kwargs and kwargs['title']:
            self.title = kwargs['title']
        else:
            self.title = self.name + "-" + self.vid

        info = json.loads(get_content('http://api.aixifan.com/plays/{}/realSource'.format(self.vid), headers = acorg_headers))
        video = info['data']['files']

        for v in video:
            self.stream_types.append(v['description'])
            self.streams[v['description']] = {'container': 'mp4', 'video_profile': v['description'], 'src' : v['url'], 'size': 0}

        self.stream_types.reverse()

site = Acorig()
