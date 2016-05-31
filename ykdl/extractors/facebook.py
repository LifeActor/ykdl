#!/usr/bin/env python

from ..extractor import VideoExtractor
import json
from urllib import parse

class Facebook(VideoExtractor):

    name = 'Facebook'

    supported_stream_types = [ 'hd_src', 'sd_src' ]

    def prepare(self):

        html = get_content(self.url)
        self.title = match1(html, '<title id="pageTitle">(.+) \| Facebook</title>')
        s2 = parse.unquote(unicodize(match1(html, '\["params","([^"]*)"\]')))
        data = json.loads(s2)
        video_data = data["video_data"]["progressive"]
        available_stream_types = video_data.keys()
        for stream in self.supported_stream_types:
            if stream in available_stream_types:
                url = video_data[0][stream]
                _, ext, size = url_info(url)
                self.stream_types.append(stream)
                self.streams[stream] = {'container': ext, 'src': [url], 'size' : size}

site = Facebook()
