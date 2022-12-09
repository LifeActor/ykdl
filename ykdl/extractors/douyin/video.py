# -*- coding: utf-8 -*-

from .._common import *


class Douyin(Extractor):
    name = '抖音 (Douyin)'

    def prepare_mid(self):
        return match1(self.url, '(?:video/|vid=)(\d+)')

    def prepare(self):
        info = MediaInfo(self.name)

        data = get_response('https://www.douyin.com/web/api/v2/aweme/iteminfo/',
                            params={'item_ids': self.mid}).json()
        assert not data['filter_list'], data['filter_list'][0]['filter_reason']

        video_info = data['item_list'][0]
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
