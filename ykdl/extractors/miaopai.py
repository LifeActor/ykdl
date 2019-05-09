#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content, url_info
from ykdl.util.match import match1, matchall
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo

import json

api_info = 'http://api.miaopai.com/m/v2_channel.json?fillType=259&scid={}&vend='
api_stream = 'http://gslb.miaopai.com/stream/{}.json?vend='

class Miaopai(VideoExtractor):

    name = u'秒拍 (Miaopai)'

    def prepare(self):
        info = VideoInfo(self.name)
        html = None
        title = None

        if not self.vid:
            self.vid = match1(self.url, '/show(?:/channel)?/([^\./]+)',
                                        '/media/([^\./]+)')
        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, 's[cm]id ?= ?[\'"]([^\'"]+)[\'"]')
        assert self.vid, "No VID match!"
        info.title = self.name + '_' + self.vid

        try:
            data = json.loads(get_content(api_info.format(self.vid)))
            assert data['status'] == 200, data['msg']

            data = data['result']
            title = data['ext']['t']
            scid = data['scid'] or self.vid
            ext = data['stream']['and']
            base = data['stream']['base']
            vend = data['stream']['vend']
            url = '{}{}.{}?vend={}'.format(base, scid, ext, vend)
        except:
            # fallback
            data = json.loads(get_content(api_stream.format(self.vid)))
            assert data['status'] == 200, data['msg']

            data = data['result'][0]
            ext = None
            scheme = data['scheme']
            host = data['host']
            path = data['path']
            sign = data['sign']
            url = '{}{}{}{}'.format(scheme, host, path, sign)

        if not title:
            if not html:
                html = get_content(self.url)
            title = match1(html, '<meta name="description" content="([^"]+)">')
        if title:
            info.title = title

        info.stream_types.append('current')
        info.streams['current'] = {
            'container': ext or 'mp4',
            'src': [url],
            'size' : 0
        }
        return info

    def prepare_list(self):
        html = get_content(self.url)
        video_list = match1(html, 'video_list=\[([^\]]+)')
        return matchall(video_list, ['\"([^\",]+)'])

site = Miaopai()
