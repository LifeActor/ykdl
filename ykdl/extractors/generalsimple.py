#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.videoinfo import VideoInfo
from ykdl.extractor import VideoExtractor
from ykdl.util.match import match1
from ykdl.util.html import get_content, url_info


class GeneralSimple(VideoExtractor):
    name = 'GeneralSimple (通用简单)'

    def pparser(self, u):
        return self.info

    def prepare(self):
        info = VideoInfo(self.name)

        html = get_content(self.url)

        info.title = match1(html, '<meta property="og:title" content="([^"]+)',
                                  '<title>(.+?)</title>')

        url = match1(html, '''(?x)
            ["'](
                (?:https?:)?//[^"']+?\.
                    (?:
                        m3u8                        | # !H5 list/HLS
                        mp4|webm                    | # video/audio
                        f4v|flv|ts                  | # !H5 video
                        mov|qt|m4[pv]|og[mv]        | # video
                        ogg|3gp|mpe?g               | # video/audio
                        mp3|flac|wave?|oga|aac|weba   # audio
                    )
                    (?:\?[^"']+)?
            )["']
        ''')
        if not url.startswith('http'):
            url = self.url[:self.url.find(':') + 1] + url

        if url:
            info.stream_types.append('current')
            info.streams['current'] = {
                'container': url_info(url)[1],
                'video_profile': 'current',
                'src': [url],
                'size': 0
            }
            self.info = info
            self.parser = self.pparser
            return info

site = GeneralSimple()
