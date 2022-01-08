# -*- coding: utf-8 -*-

from .._common import *


class TikTok(Extractor):
    name = '抖音 (TikTok)'

    def prepare(self):
        info = MediaInfo(self.name)
        vid = match1(self.url, '(?:video/|vid=)(\d+)')
        data = get_response('https://www.douyin.com/web/api/v2/aweme/iteminfo/',
                            params={'item_ids': vid}).json()

        video_info = data['item_list'][0]
        title = video_info['desc']
        nickName = video_info['author'].get('nickname', '')
        uid = video_info['author'].get('unique_id') or \
                video_info['author']['short_id']

        info.title = '{title} - {nickName}(@{uid})'.format(**vars())
        info.artist = nickName
        info.streams['current'] = {
            'container': 'mp4',
            'video_profile': 'current',
            'src' : [video_info['video']['play_addr']['url_list'][0]
                                .replace('playwm', 'play')],
        }
        return info

site = TikTok()
