#!/usr/bin/env python

from ..common import *
from ..extractor import VideoExtractor
import json

class Qianmo(VideoExtractor):
    name = "阡陌 (qianmo)"

    stream_types = [
        {'id': 'hd', 'container': 'mp4', 'video_profile': 'hd'},
    ]

    def prepare(self, **kwargs):
        assert self.url or self.vid

        if self.url and not self.vid:
            html = get_html(self.url)
            match = re.search(r'(.+?)var video =(.+?);', html)
            if match:
                video_info_json = json.loads(match.group(2))
                self.title = video_info_json['title']
                self.vid = video_info_json['ext_video_id']
            else:
                raise ValueError
        else:
            self.title = title or self.vid

        html = get_content('http://v.qianmo.com/player/{}'.format(self.vid))
        c = json.loads(html)
        for stream in self.stream_types:
            if stream['id'] in c['seg'].keys():
                urls = []
                size = 0
                for info in c['seg'][stream['id']][0]['url']:
                    size += url_size(info[0])
                    urls.append(info[0])
                self.streams[stream['id']] = {'container': 'mp4','video_profile': stream['video_profile'], 'src': urls, 'size' : size}

site = Qianmo()
download = site.download_by_url
download_playlist = playlist_not_supported('qianmo')
