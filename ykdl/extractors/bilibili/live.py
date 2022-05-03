# -*- coding: utf-8 -*-

from .._common import *


class BiliLive(Extractor):
    name = 'Bilibili live (哔哩哔哩 直播)'

    profile_2_id = {
        '4K':   '4K',
        '原画': 'OG',
        '蓝光': 'BD',
        '超清': 'TD',
        '高清': 'HD',
        '流畅': 'SD'
    }

    def prepare(self):
        info = MediaInfo(self.name, True)

        ID = match1(self.url, '/(\d+)')
        api1_data = get_response(
                'https://api.live.bilibili.com/room/v1/Room/room_init',
                params={'id': ID}).json()
        if api1_data['code'] == 0:
            self.vid = api1_data['data']['room_id']
        else:
            self.logger.debug('Get room ID from API failed: %s', api1_data['msg'])
            self.vid = ID

        api2_data = get_response(
                'https://api.live.bilibili.com/room/v1/Room/get_info',
                params={'room_id': self.vid}).json()
        assert api2_data['code'] == 0, api2_data['msg']
        api2_data = api2_data['data']
        assert api2_data['live_status'] == 1, '主播正在觅食......'
        info.title = title = api2_data['title']

        api3_data = get_response(
                'https://api.live.bilibili.com/live_user/v1/UserInfo/get_anchor_in_room',
                params={'roomid': self.vid}).json()
        if api3_data['code'] == 0:
            info.artist = artist = api3_data['data']['info']['uname']
            info.title = '{title} - {artist}'.format(**vars())

        def get_live_info(qn=1):
            data = get_response(
                    'https://api.live.bilibili.com/xlive/web-room/v2/index/getRoomPlayInfo',
                    params={
                        'room_id': self.vid,
                        'protocol': '0,1',    # 0 = http_stream, 1 = http_hls
                        'format': '0,1,2',
                        'codec': '0',         # 0 = avc, 1 = hevc
                        'qn': qn,
                        'platform': 'web',
                        'ptype': 8,
                        'dolby': 5
                    }).json()

            assert data['code'] == 0, data['msg']

            data = data['data']['playurl_info']['playurl']
            g_qn_desc = {x['qn']: x['desc'] for x in data['g_qn_desc']}
            stream = random.choice(data['stream'])
            format = random.choice(stream['format'])
            codec = random.choice(format['codec'])
            url_info = random.choice(codec['url_info'])
            urls = [url_info['host']+codec['base_url']+url_info['extra']]
            qlt = codec['current_qn']
            aqlts = {x: g_qn_desc[x] for x in codec['accept_qn']}
            size = float('inf')
            ext = format['format_name']
            prf = aqlts[qlt]
            st = self.profile_2_id[prf]
            if urls:
                info.streams[st] = {
                    'container': ext,
                    'video_profile': prf,
                    'src' : urls,
                    'size': size
                }

            if qn == 1:
                del aqlts[qlt]
                for aqlt in aqlts:
                    get_live_info(aqlt)

        get_live_info()
        return info

site = BiliLive()
