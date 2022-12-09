# -*- coding: utf-8 -*-

from ._common import *


class Kuwo(Extractor):
    name = 'KuWo (酷我音乐)'

    def prepare_mid(self):
        return match1(self.url, '/play_detail/(\d+)')

    def prepare(self):
        info = MediaInfo(self.name)
        install_cookie()

        if not self.is_list:
            resp = get_response('https://www.kuwo.cn/favicon.ico?v=1')
        kw_token = get_cookie('www.kuwo.cn', '/', 'kw_token').value
        params = {
            'mid': self.mid,
            'httpsStatus': 1,
            'reqId': get_random_uuid()
        }
        data = get_response('https://www.kuwo.cn/api/www/music/musicInfo',
                            headers={'csrf': kw_token},
                            params=params).json()
        assert data.get('code') == 200, data['message']
        data = data['data']

        pay = data['isListenFee']
        if pay:
            if self.is_list:  # just skip pay when extract from list
                self.logger.warning('Skip pay song: %s', self.mid)
                return
            raise AssertionError('Pay song: %s' % self.mid)

        albumpic = data['albumpic']
        album = data['album']
        title = data['name']
        info.title = album in title and title or '{title} - {album}'.format(**vars())
        info.artist = data['artist']
        info.album = data['album']
        info.duration = data['duration']
        info.add_comment(data['albuminfo'])

        params['type'] = 'music'
        data = get_response('https://www.kuwo.cn/api/v1/www/music/playUrl',
                            params=params).json()
        assert data.get('code') == 200, data['message']

        url = data['data']['url']
        info.streams['current'] = {
            'container': 'mp3',
            'profile': 'current',
            'src': [url]
        }
        return info

    def list_only(self):
        return 'playlist_detail' in self.url

    def prepare_list(self):
        install_cookie()
        html = get_content(self.url)
        return matchall(html, 'href="/play_detail/(\d+)"')

site = Kuwo()
