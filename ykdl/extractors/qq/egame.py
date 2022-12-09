# -*- coding: utf-8 -*-

from .._common import *


assert JSEngine, "No JS Interpreter found, can't extract egame live!"


class QQEGame(Extractor):
    name = 'QQ EGAME (企鹅电竟)'

    lv_2_id = {
        10: 'BD10M',
         8: 'BD8M',
         6: 'BD6M',
         4: 'BD4M',
         3: 'TD',
         2: 'HD',
         1: 'SD',
    }

    @staticmethod
    def format_mid(mid):
        mid = fullmatch(mid, '\d+')
        assert mid
        return mid

    def prepare_mid(self):
        return match1(self.url, '/(\d+)')

    def prepare(self):
        info = MediaInfo(self.name, True)

        if self.url is None:
            self.url = 'https://egame.qq.com/' + self.mid
        html = get_content(self.url)

        js_nuxt = match1(html, '<script>window.__NUXT__=(.+?)</script>')
        js_ctx = JSEngine()
        data = js_ctx.eval(js_nuxt)
        self.logger.debug('data:\n%s', data)

        state = data.get('state', {})
        error = data.get('error') or state.get('errors')
        assert not error, 'error: {error}!!'.format(**vars())

        liveInfo = state['live-info']['liveInfo']
        videoInfo = liveInfo['videoInfo']
        profileInfo = liveInfo['profileInfo']
        assert profileInfo['isLive'], 'error: live show is not on line!!'

        title = videoInfo['title']
        info.artist = artist = profileInfo['nickName']
        info.title = '{title} - {artist}'.format(**vars())

        for s in videoInfo['streamInfos']:
            stream_id = self.lv_2_id[s['levelType']]
            info.streams[stream_id] = {
                'container': 'flv',
                'profile': s['desc'],
                'src' : [s['playUrl']],
                'size': Infinity
            }

        return info


site = QQEGame()
