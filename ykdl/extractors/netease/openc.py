#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.util.match import match1
from ykdl.util.html import get_content
from ykdl.util.jsengine import JSEngine

assert JSEngine, "No JS Interpreter found, can't parse douyu live/video!"

class OpenC(VideoExtractor):
    name = "网易公开课 (163 openCourse)"

    sopported_stream_types = [
        ['TD', 'Shd', '超清'], 
        ['HD',  'Hd', '高清'], 
        ['SD',  'Sd', '标清']
    ]

    def list_only(self):
        self.vid = match1(self.url, 'mid=(\w+)')
        return self.vid is None

    def prepare_data(self):
        html = get_content(self.url)
        js = match1(html, 'window\.__NUXT__=(.+);</script>')
        js_ctx = JSEngine()
        self.data = js_ctx.eval(js)
        self.logger.debug('video_data: \n%s', self.data)

    def prepare(self):
        info = VideoInfo(self.name)

        if self.data is None:
            self.prepare_data()
        data = self.data
        if self.vid is None:
            movie = data['state']['movie']['moiveList'][0]
        else:
            for movie in data['state']['movie']['moiveList']:
                mid = movie['mid']
                if mid == self.vid:
                    break
            assert mid == self.vid, 'can not found mid %r' % mid

        title = data['data'][0]['title']
        mtitle = movie['title']
        school = data['data'][0]['school']
        director = data['data'][0]['director']
        if mtitle.startswith(title):
            title = mtitle
        elif mtitle != title:
            title = '{} - {}'.format(title, mtitle)
        if school not in title:
            title = '{} - {}'.format(title, school)
        info.title = title
        info.artist = director

        for stream, tp, profile in self.sopported_stream_types:
            for ext in ['mp4', 'm3u8']:
                for orig in ['', 'Orign']:
                    if stream in info.streams:
                        continue
                    url = movie['{}{}Url{}'.format(ext, tp, orig)]
                    if not url:
                        continue
                    size = movie['{}{}Size{}'.format(ext, tp, orig)]
                    info.stream_types.append(stream)
                    info.streams[stream] = {
                        'container': ext,
                        'video_profile': profile,
                        'src' : [url],
                        'size': size
                    }

        if movie['subList']:
            url = movie['mp4ShareUrl']
            if url:
                info.stream_types.insert(0, 'subtitle')
                info.streams['subtitle'] = {
                    'container': 'mp4',
                    'video_profile': '有字幕',
                    'src' : [url],
                    'size': 0
                }

        return info

    def prepare_list(self):
        self.prepare_data()
        return [movie['mid'] for movie in self.data['state']['movie']['moiveList']]

site = OpenC()
