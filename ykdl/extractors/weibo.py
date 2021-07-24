#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.util.html import fake_headers, add_header, get_content
from ykdl.util.match import match1
from urllib.parse import urlencode, unquote

import json

API = 'https://weibo.com/tv/api/component'
add_header('User-Agent', 'Baiduspider')

class Weibo(VideoExtractor):
    name = "微博 (Weibo)"

    ids = ['4K', '2K', 'BD', 'TD', 'HD', 'SD', 'current']
    quality_2_id = {
           '4': '4K',
           '2': '2K',
        '1080': 'BD',
         '720': 'TD',
         '480': 'HD',
         '360': 'SD'
    }

    def prepare(self):
        info = VideoInfo(self.name)

        def append_stream(video_profile, video_quality, url):
            stream_id = self.quality_2_id[video_quality]
            if stream_id in info.stream_types:
                return
            info.stream_types.append(stream_id)
            info.streams[stream_id] = {
                'video_profile': video_profile,
                'container': 'mp4',
                'src' : [url]
            }

        self.vid = match1(self.url, '\D(\d{4}:(?:\d{16}|\w{32}))(?:\W|$)')

        if self.vid is None:
            page = match1(self.url, 'https?://[^/]+(/\d+/\w+)')
            if page is None or match1(page, '/(\d+)$'):
                html = get_content(self.url.replace('//weibo.', '//hk.weibo.')
                                           .replace('/user/', '/'))
                page = match1(html, '"og:url".+weibo.com(/\d+/\w+)')
            assert page, 'can not find any video!!!'
            html = get_content('https://weibo.com' + page)
            streams = match1(html, 'quality_label_list=([^"]+)').split('&')[0]
            if streams:
                streams = json.loads(unquote(streams))
                for stream in streams:
                    video_quality = stream['quality_label'].upper()
                    video_profile = stream['quality_desc'] + ' ' + video_quality
                    video_quality = match1(video_quality, '(\d+)')
                    append_stream(video_profile, video_quality, stream['url'])
            else:
                url = match1(html, 'action-data="[^"]+?&video_src=([^"&]+)')
                if url:
                    info.stream_types.append('current')
                    info.streams['current'] = {
                        'video_profile': 'current',
                        'container': 'mp4',
                        'src' : [unquote(url)]
                    }
            if info.streams:
                info.title = match1(html, '<meta content="([^"]+)" name="description"').split('\n')[0]
                info.artist = match1(html, '<meta content="([^"]+)" name="keywords"').split(',')[0]
                i = info.title.find('】') + 1
                if i:
                    info.title = info.title[:i]
            else:
                self.vid = match1(html, 'objectid=(\d{4}:(?:\d{16}|\w{32}))\W')
                assert self.vid, 'can not find any video!!!'

        if self.vid:
            headers = {'Referer': 'https://weibo.com/tv/show/' + self.vid}
            headers.update(fake_headers)
            data = urlencode({
                'data': json.dumps({
                    'Component_Play_Playinfo': {'oid': self.vid}
                })
            }).encode()
            vdata = get_content(API, headers=headers, data=data)
            vdata = json.loads(vdata)['data']['Component_Play_Playinfo']
            info.title = vdata['title']
            info.artist = vdata['author']
            for video_profile, url in vdata['urls'].items():
                if url:
                    video_quality = match1(video_profile, '(\d+)')
                    append_stream(video_profile, video_quality, 'https:' + url)

        info.stream_types = sorted(info.stream_types, key=self.ids.index)
        return info

site = Weibo()
