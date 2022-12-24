# -*- coding: utf-8 -*-

from .._common import *


class Douyin(Extractor):
    name = '抖音 (Douyin)'

    def prepare_mid(self):
        return match1(self.url, '(?:video/|vid=)(\d+)')

    def prepare(self):
        info = MediaInfo(self.name)

        data = get_response('https://www.iesdouyin.com/aweme/v1/web/aweme/detail/',
                            params={'aweme_id': self.mid}).json()
        assert data['status_code'] == 0, data['status_msg']
        assert data['aweme_detail'], data['filter_detail']

        video_info = data['aweme_detail']
        title = video_info['desc']
        nickName = video_info['author'].get('nickname', '')
        uid = video_info['author'].get('unique_id') or \
                video_info['author']['short_id']

        info.title = '{title} - {nickName}(@{uid})'.format(**vars())
        info.artist = nickName
        info.duration = video_info['duration'] // 1000

        info.streams['current'] = {
            'container': 'mp4',
            'profile': video_info['video']['ratio'].upper(),
            'src': [video_info['video']['play_addr']['url_list'][0]
                              .replace('playwm', 'play')]
        }
        return info

site = Douyin()
