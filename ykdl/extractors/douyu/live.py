# -*- coding: utf-8 -*-

from .._common import *
from .util import get_h5enc, ub98484234


class Douyutv(Extractor):
    name = '斗鱼直播 (DouyuTV)'

    profile_2_id = {
        '原画':    'OG',
        '蓝光10M': 'BD10M',
        '蓝光8M':  'BD8M',
        '蓝光4M':  'BD4M',
        '蓝光':    'BD',
        '超清':    'TD',
        '高清':    'HD',
        '流畅':    'SD'
     }

    def prepare_mid(self):
        html = get_content(self.url)
        mid = match1(html, '\$ROOM\.room_id\s*=\s*(\d+)',
                           'room_id\s*=\s*(\d+)',
                           '"room_id.?":(\d+)',
                           'data-onlineid=(\d+)',
                           '(房间已被关闭)')
        assert mid != '房间已被关闭', '房间已被关闭'
        return mid

    def prepare(self):
        info = MediaInfo(self.name, True)

        add_header('Referer', 'https://www.douyu.com')
        html = get_content(self.url)

        title = match1(html, 'Title-head\w*">([^<]+)<')
        artist = match1(html, 'Title-anchorName\w*" title="([^"]+)"')
        if not title or not artist:
            room_data = get_response(
                    'https://open.douyucdn.cn/api/RoomApi/room/' + self.mid
                    ).json()
            if room_data['error'] == 0:
                room_data = room_data['data']
                title = room_data['room_name']
                artist = room_data['owner_name']

        info.title = '{title} - {artist}'.format(**vars())
        info.artist = artist

        js_enc = get_h5enc(html, self.mid)
        params = {
            'cdn': '',
            'iar': 0,
            'ive': 0,
        }
        ub98484234(js_enc, self.mid, self.logger, params)

        def get_live_info(rate=0):
            params['rate'] = rate
            live_data = get_response(
                        'https://www.douyu.com/lapi/live/getH5Play/' + self.mid,
                        data=params).json()
            if live_data['error']:
                return live_data['msg']

            live_data = live_data['data']
            real_url = '/'.join([live_data['rtmp_url'], live_data['rtmp_live']])
            rate_2_profile = {rate['rate']: rate['name']
                              for rate in live_data['multirates']}
            stream_profile = rate_2_profile[live_data['rate']]
            if '原画' in stream_profile:
                stream_id = 'OG'
            else:
                stream_id = self.profile_2_id[stream_profile]
            info.streams[stream_id] = {
                'container': match1(live_data['rtmp_live'], '\.(\w+)\?'),
                'profile': stream_profile,
                'src' : [real_url],
                'size': Infinity
            }

            error_msges = []
            if rate == 0:
                rate_2_profile.pop(0, None)
                rate_2_profile.pop(live_data['rate'], None)
                for rate in rate_2_profile:
                    error_msg = get_live_info(rate)
                    if error_msg:
                        error_msges.append(error_msg)
            if error_msges:
                return ', '.join(error_msges)

        error_msg = get_live_info()
        if error_msg:
            self.logger.debug('error_msg:\n\t' + error_msg)

        return info

    def prepare_list(self):
        html = get_content(self.url)
        return matchall(html, 'class="hroom_id" value="([^"]+)',
                              'data-room_id="([^"]+)')

site = Douyutv()
