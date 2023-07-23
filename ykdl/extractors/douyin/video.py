# -*- coding: utf-8 -*-

from .._common import *


class Douyin(Extractor):
    name = '抖音 (Douyin)'

    def prepare_mid(self):
        return match1(self.url, r'\b(?:video/|music/|vid=|aweme_id=|item_ids=)(\d+)')

    def prepare(self):
        info = MediaInfo(self.name)

        data = get_response('https://www.iesdouyin.com/aweme/v1/web/aweme/detail/',
                            params={'aweme_id': self.mid}).json()
        assert data['status_code'] == 0, data['status_msg']
        assert data['aweme_detail'], data['filter_detail']

        data = data['aweme_detail']
        aweme_type = data['aweme_type']
        # TikTok [0, 51, 55, 58, 61, 150]
        if aweme_type not in [2, 68, 150, 0, 4, 51, 55, 58, 61]:
            print('new type', aweme_type)
        music_image = aweme_type in [2, 68, 150]  # video [0, 4, 51, 55, 58, 61]
        title = data['desc']
        nickName = data['author'].get('nickname', '')
        uid = data['author'].get('unique_id') or \
                data['author']['short_id']

        info.title = '{title} - {nickName}(@{uid})'.format(**vars())
        info.artist = nickName
        info.duration = data['duration'] // 1000

        ext = 'mp4'
        url = data['video']['play_addr']['url_list'][0] \
                        .replace('playwm', 'play')
        if music_image or 'music' in url:
            ext = 'mp3'
            url = data['video']['cover']['url_list'][0], url
        info.streams['current'] = {
            'container': ext,
            'profile': data['video']['ratio'].upper(),
            'src': [url]
        }
        return info

site = Douyin()
