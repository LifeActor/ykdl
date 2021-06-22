#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content, add_header
from ykdl.util.match import match1
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo

import json
from urllib.parse import unquote


class TikTok(VideoExtractor):
    name = '抖音直播 (TikTok)'

    stream_ids = ['OG', 'BD', 'TD', 'HD', 'SD']
    profile_2_id = {
        '原画': 'OG',
        '蓝光': 'BD',
        '超清': 'TD',
        '高清': 'HD',
        '标清': 'SD'
     }

    def prepare(self):
        info = VideoInfo(self.name)

        html = get_content(self.url)
        data = match1(html, 'type="application/json">(.+?)</script>')
        data = json.loads(unquote(data))

        video_info = data['routeInitialProps']['roomInfo'].get('room')
        assert video_info, 'live is off!!!'

        title = video_info['title']
        nickName = video_info['owner']['nickname']
        info.title = '{title} - {nickName}'.format(**vars())
        info.artist = nickName

        stream_info = video_info['stream_url']
        stream_name = stream_info['resolution_name']
        stream_url = stream_info['flv_pull_url']
        stream_url['ORIGION'] = stream_info['rtmp_pull_url']
        
        for ql, url in stream_url.items():
            video_profile = stream_name[ql]
            stream = self.profile_2_id[video_profile]
            info.stream_types.append(stream)
            info.streams[stream] = {
                'container': 'flv',
                'video_profile': video_profile,
                'src' : [url],
            }

        info.stream_types = sorted(info.stream_types, key=self.stream_ids.index)
        return info

site = TikTok()
