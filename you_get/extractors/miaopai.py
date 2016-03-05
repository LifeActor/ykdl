#!/usr/bin/env python

from ..util.html import *
from ..util.match import *
from ..util import log
from ..extractor import VideoExtractor

import json

class Miaopai(VideoExtractor):

    name = '秒拍 (Miaopai)'

    def prepare(self, **kwargs):
        assert self.url or self.vid

        if not self.vid:
            self.vid = match1(self.url, 'http://www.miaopai.com/show/channel/([^.]+)', \
                                        'http://www.miaopai.com/show/([^.]+)', \
                                        'http://m.miaopai.com/show/channel/([^.]+)')
        content = json.loads(get_content('http://api.miaopai.com/m/v2_channel.json?fillType=259&scid={}&vend=miaopai'.format(self.vid)))
        if content['status'] != 200:
            log.wtf("something error!")
        content = content['result']
        self.title = content['ext']['t']
        url = content['stream']['base']
        ext = content['stream']['and']

        self.stream_types.append('current')
        self.streams['current'] = {'container': ext, 'src': [url], 'size' : 0}

    def download_playlist_by_url(self, url, param, **kwargs):
        html = get_content(url)
        video_list = match1(html, 'video_list=\[([^\]]+)')
        vids = matchall(video_list, ['\"([^\",]+)'])
        for vid in vids:
            self.download_by_vid(vid, param, **kwargs)

site = Miaopai()
download = site.download_by_url
download_playlist = site.download_playlist_by_url
