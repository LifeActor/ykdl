#!/usr/bin/env python

from ..common import *
from ..extractor import VideoExtractor
import json

class Facebook(VideoExtractor):

    name = 'Facebook'

    supported_stream_types = [ 'hd_src', 'sd_src' ]

    def prepare(self, **kwargs):
        assert self.url

        html = get_content(self.url)
        self.title = match1(html, '<title id="pageTitle">(.+) \| Facebook</title>')
        s2 = parse.unquote(unicodize(r1(r'\["params","([^"]*)"\]', html)))
        data = json.loads(s2)
        video_data = data["video_data"][0]
        available_stream_types = video_data.keys()
        for stream in self.supported_stream_types:
            if stream in available_stream_types:
                url = video_data[stream]
                _, ext, size = url_info(url)
                self.stream_types.append(stream)
                self.streams[stream] = {'container': ext, 'src': [url], 'size' : size}

    def download_by_vid(self):
        pass

site = Facebook()
download = site.download_by_url
download_playlist = playlist_not_supported('facebook')
