#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.html import *
from ..util.match import *
from ykdl.util.m3u8_wrap import load_m3u8_playlist
from ..extractor import VideoExtractor

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

        self.title = match1(html, '<title>([^<]+)').split("_")[0]
        if self.live:
            rtmp_id = match1(html, 'videoId":"([^"]+)"').replace('\\/','/')
            real_url = self.live_base+'/'+rtmp_id+'.m3u8'
            self.stream_types, self.streams = load_m3u8_playlist(real_url)
        else:
            vod_m3u8 = self.vod_base + '/' + match1(html, 'VideoID":"([^"]+)').replace('\\/','/')
            self.stream_types.append('current')
            self.streams['current'] = {'container': 'm3u8', 'video_profile': 'current', 'src' : [vod_m3u8], 'size': 0}

site = Zhanqi()
