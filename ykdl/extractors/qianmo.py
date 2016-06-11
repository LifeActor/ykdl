#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.html import get_content, url_size
from ..extractor import VideoExtractor
import json
import re

class Qianmo(VideoExtractor):
    name = u"阡陌 (qianmo)"

    supported_stream_types = [ 'hd' ]


    def prepare(self):

        if self.url and not self.vid:
            html = get_content(self.url)
            match = re.search(r'(.+?)var video =(.+?);', html)
            if match:
                video_info_json = json.loads(match.group(2))
                self.title = video_info_json['title']
                self.vid = video_info_json['ext_video_id']
            else:
                raise ValueError

        html = get_content('http://v.qianmo.com/player/{}'.format(self.vid))
        c = json.loads(html)
        for stream in self.supported_stream_types:
            if stream in c['seg'].keys():
                urls = []
                size = 0
                for info in c['seg'][stream][0]['url']:
                    size += url_size(info[0])
                    urls.append(info[0])
                self.streams[stream['id']] = {'container': 'mp4','video_profile': stream, 'src': urls, 'size' : size}
                self.stream_types.append(stream)

site = Qianmo()
