#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content, url_info
from ykdl.util.match import match1, matchall
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo

import json

class Miaopai(VideoExtractor):

    name = u'秒拍 (Miaopai)'

    def prepare(self):
        info = VideoInfo(self.name)
        if not self.vid:
            self.vid = match1(self.url, '/show(?:/channel)?/([^\./]+)',
                                        '/media/([^\./]+)')
        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, 's[cm]id ?= ?[\'"]([^\'"]+)[\'"]')
        assert self.vid, "No VID match!"

        data = json.loads(get_content('https://n.miaopai.com/api/aj_media/info.json?smid={}'.format(self.vid)))
        assert data['code'] == 200, data['msg']

        data = data['data']
        info.title = data['description'] or self.name + '_' + self.vid
        url = data['meta_data'][0]['play_urls']['m']
        _, ext, _ = url_info(url)

        info.stream_types.append('current')
        info.streams['current'] = {'container': ext or 'mp4', 'src': [url], 'size' : 0}
        return info

    def prepare_list(self):
        html = get_content(self.url)
        video_list = match1(html, 'video_list=\[([^\]]+)')
        return matchall(video_list, ['\"([^\",]+)'])

site = Miaopai()
