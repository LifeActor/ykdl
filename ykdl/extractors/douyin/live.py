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
    quality_2_profile_id = {
        'ORIGION': ['原画', 'OG'],
        'FULL_HD1': ['蓝光', 'BD'],
        'HD1': ['超清', 'TD'],
        'SD1': ['高清', 'HD'],
        'SD2': ['标清', 'SD']
     }

    def prepare(self):
        info = VideoInfo(self.name)

        html = get_content(self.url)
        data = match1(html, 'id="RENDER_DATA" type="application/json">(.+?)</script>',
                            '__INIT_PROPS__ = (.+?)</script>')
        data = json.loads(unquote(data))
        self.logger.debug('data: \n%s', data)

        try:
            video_info = data['initialState']['roomStore']['roomInfo'].get('room')
        except KeyError:
            video_info = data['/webcast/reflow/:id'].get('room')
        assert video_info and video_info['status'] == 2, 'live is off!!!'

        title = video_info['title']
        nickName = video_info['owner']['nickname']
        info.title = '{title} - {nickName}'.format(**vars())
        info.artist = nickName

        stream_info = video_info['stream_url']
        stream_url = stream_info['flv_pull_url']
        stream_url['ORIGION'] = stream_info.get('rtmp_pull_url')
        
        for ql, url in stream_url.items():
            if not url:
                continue
            video_profile, stream = self.quality_2_profile_id[ql]
            info.stream_types.append(stream)
            info.streams[stream] = {
                'container': 'flv',
                'video_profile': video_profile,
                'src' : [url],
            }

        info.stream_types = sorted(info.stream_types, key=self.stream_ids.index)
        return info

site = TikTok()
