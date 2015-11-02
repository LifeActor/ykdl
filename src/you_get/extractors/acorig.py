#!/usr/bin/env python
from ..common import playlist_not_supported
from ..extractor import VideoExtractor
from ..util.html import get_content
import json

class Acorig(VideoExtractor):
    name = "AcFun 原创"

    def prepare(self, **kwargs):
        assert self.url or self.vid

        if 'title' in kwargs and kwargs['title']:
            self.title = kwargs['title']
        else:
            self.title = self.name + "-" + self.vid

        info = json.loads(get_content('http://www.acfun.tv/video/getVideo.aspx?id=' + self.vid))

        urls = []
        for v in info['videoList']:
            urls.append(v['playUrl'])

        self.stream_types.append('current')
        self.streams['current'] = {'container': 'mp4', 'video_profile': 'current', 'src' : urls, 'size': 0}

site = Acorig()
download = site.download_by_url
download_playlist = playlist_not_supported('AcFun')
