#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.html import *
from ..util.match import *
from ykdl.util.m3u8_wrap import load_m3u8_playlist
from ..extractor import VideoExtractor
import re

class Zhanqi(VideoExtractor):
    name = u'战旗 (zhanqi)'

    live = False

    live_base = "http://dlhls.cdn.zhanqi.tv/zqlive/"
    vod_base = "http://dlvod.cdn.zhanqi.tv"
    def prepare(self):

        html = get_content(self.url)
        video_type = match1(html, 'VideoType":"([^"]+)"')
        if video_type == 'LIVE':
            self.live = True
        elif not video_type == 'VOD':
            NotImplementedError('Unknown_video_type')

        self.title = match1(html, '<title>([^<]+)')
        if self.live:
            rtmp_id = match1(html, 'videoId":"([^"]+)"').replace('\\/','/')
            real_url = self.live_base+'/'+rtmp_id+'.m3u8'
            self.stream_types, self.streams = load_m3u8_playlist(real_url)
        else:
            vod_m3u8_request = self.vod_base + match1(html, 'VideoID":"([^"]+)').replace('\\/','/')
            vod_m3u8 = get_content(vod_m3u8_request)
            part_url = re.findall(r'(/[^#]+)\.ts',vod_m3u8)
            real_url = []
            for i in part_url:
                i = self.vod_base + i + ".ts"
                real_url.append(i)
            type_ = ''
            size = 0
            for url in real_url:
                _, type_, temp = url_info(url)
                size += temp or 0
            self.stream_types.append('current')
            self.streams['current'] = {'container': 'flv', 'video_profile': 'current', 'src' : real_url, 'size': size}

site = Zhanqi()
