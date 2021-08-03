#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content, add_header
from ykdl.util.match import match1
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo

import json
from urllib.parse import unquote


class TikTok(VideoExtractor):
    name = '抖音 (TikTok)'

    def prepare(self):
        info = VideoInfo(self.name)
        vid = match1(self.url, '(?:video/|vid=)(\d+)')
        data = get_content('https://www.douyin.com/web/api/v2/aweme/iteminfo/?item_ids=' + vid)
        data = json.loads(data)

        video_info = data['item_list'][0]
        title = video_info['desc']
        nickName = video_info['author'].get('nickname', '')
        uid = video_info['author'].get('unique_id') or video_info['author']['short_id']

        info.title = '{title} - {nickName}(@{uid})'.format(**vars())
        info.artist = nickName
        info.stream_types.append('current')
        info.streams['current'] = {
            'container': 'mp4',
            'video_profile': 'current',
            'src' : [video_info['video']['play_addr']['url_list'][0].replace('playwm', 'play')],
        }
        return info

site = TikTok()
