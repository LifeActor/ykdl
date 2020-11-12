#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.util.jsengine import JSEngine

assert JSEngine, "No JS Interpreter found, can't parse egame live!"


class QQEGame(VideoExtractor):
    name = u'QQ EGAME (企鹅电竟)'

    stream_ids = ['BD10M', 'BD8M', 'BD6M', 'BD4M', 'BD', 'TD', 'HD', 'SD']
    
    lv_2_id = {
        10: 'BD10M',
         8: 'BD8M',
         6: 'BD6M',
         4: 'BD4M',
         3: 'TD',
         2: 'HD',
         1: 'SD',
    }

    def prepare(self):
        info = VideoInfo(self.name, True)
        if not self.vid:
            self.vid = match1(self.url, '/(\d+)')
        if not self.url:
            self.url = 'https://egame.qq.com/' + self.vid
        html = get_content(self.url)

        js_nuxt = match1(html, '<script>window.__NUXT__=(.+?)</script>')
        js_ctx = JSEngine()
        data = js_ctx.eval(js_nuxt)
        self.logger.debug('data => %s', data)

        state = data.get('state', {})
        error = data.get('error') or state.get('errors')
        assert not error, 'error: {}!!'.format(error)

        liveInfo = state['live-info']['liveInfo']
        videoInfo = liveInfo['videoInfo']
        profileInfo = liveInfo['profileInfo']
        assert profileInfo['isLive'], 'error: live show is not on line!!'

        title = videoInfo['title']
        info.artist = artist = profileInfo['nickName']
        info.title = u'{} - {}'.format(title, artist)

        for s in videoInfo['streamInfos']:
            stream = self.lv_2_id[s['levelType']]
            info.stream_types.append(stream)
            info.streams[stream] = {
                'container': 'flv',
                'video_profile': s['desc'],
                'src': [s['playUrl']],
                'size': float('inf')
            }

        info.stream_types = sorted(info.stream_types, key=self.stream_ids.index)
        return info


site = QQEGame()
