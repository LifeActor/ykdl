#!/usr/bin/env python
from ..common import *
from ..extractor import VideoExtractor
import re

class Zhanqi(VideoExtractor):
    name = '战旗 (zhanqi)'

    live = False

    live_base = "http://wshdl.load.cdn.zhanqi.tv/zqlive"
    vod_base = "http://dlvod.cdn.zhanqi.tv"
    def prepare(self, **kwargs):
        assert self.url

        html = get_content(self.url)
        video_type = match1(html, 'VideoType":"([^"]+)"')
        if video_type == 'LIVE':
            self.live = True
        elif not video_type == 'VOD':
            NotImplementedError('Unknown_video_type')

        self.title = match1(html, '<title>([^<]+)')
        if self.live:
            rtmp_id = match1(html, 'videoId":"([^"]+)"').replace('\\/','/')
            request_url = self.live_base+'/'+rtmp_id+'.flv?get_url=1'
            real_url = [get_html(request_url)]
            self.stream_types.append('current')
            self.streams['current'] = {'container': 'flv', 'video_profile': 'current', 'src' : real_url, 'size': float('inf')}
        else:
            vod_m3u8_request = self.vod_base + match1(html, 'VideoID":"([^"]+)').replace('\\/','/')
            vod_m3u8 = get_html(vod_m3u8_request)
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
    def download_by_vid(self):
        pass

site = Zhanqi()
download = site.download_by_url
download_playlist = playlist_not_supported('zhanqi')
