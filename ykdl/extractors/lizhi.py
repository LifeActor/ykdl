# -*- coding: utf-8 -*-

from ._common import *


class Lizhi(Extractor):
    name = 'Lizhi FM (荔枝电台)'

    def prepare_mid(self):
        pass

    def prepare(self):
        info = MediaInfo(self.name)

        html = get_content(self.url)
        self.mid, info.artist, _, info.title = matchm(html,
                'data-hidden-ph\s?=\s?"(.+?)" '
                'data-user-name\s?=\s?"(.+?)" '
                'data-radio-name\s?=\s?"(.+?)" '
                'data-title\s?=\s?"(.+?)"')
        data = get_response('https://www.lizhi.fm/hidden_ph/{self.mid}'
                            .format(**vars())).json()
        assert data['rcode'] == 0, data['msg']

        info.streams['current'] = {
            'container': 'mp3',
            'profile': 'current',
            'src': [data['data']['url']]
        }
        return info

    def list_only(self):
        return 'user' in self.url

    def prepare_list(self):
        html = get_content(self.url)
        fm = match1(html, 'class="user-info-name">FM(\d+)')
        audio = matchall(html, 'href="(/{fm}/\d+)"'.format(**vars()))
        audio.reverse()
        return ['https://www.lizhi.fm' + a for a in audio]

site = Lizhi()
