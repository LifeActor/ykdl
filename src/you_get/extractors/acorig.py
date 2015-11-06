#!/usr/bin/env python
from ..common import playlist_not_supported
from ..extractor import VideoExtractor
from ..util.html import get_content
import json

class Acorig(VideoExtractor):
    name = "AcFun 原创"

    supported_stream_types = [ 'low', 'mid', 'high' ]

    def prepare(self, **kwargs):
        assert self.url or self.vid

        if 'title' in kwargs and kwargs['title']:
            self.title = kwargs['title']
        else:
            self.title = self.name + "-" + self.vid

        info = json.loads(get_content('http://www.acfun.tv/video/getVideo.aspx?id=' + self.vid))

        for v in info['videoList']:
            t = self.supported_stream_types[v['bitRate']-1]
            self.stream_types.append(t)
            self.streams[t] = {'container': 'mp4', 'video_profile': t, 'src' : [v['playUrl']], 'size': 0}

        self.stream_types.reverse()

site = Acorig()
download = site.download_by_url
download_playlist = playlist_not_supported('AcFun')
