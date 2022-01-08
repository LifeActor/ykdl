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
                    'https://api.live.bilibili.com/xlive/web-room/v1/playUrl/playUrl',
                    params={
                        'https_url_req': 1,
                        'cid': self.vid,
                        'platform': 'web',
                        'qn': qn,
                        'ptype': 16
                    }).json()

            assert data['code'] == 0, data['msg']

            data = data['data']
            urls = [random.choice(data['durl'])['url']]
            qlt = data['current_qn']
            aqlts = {x['qn']: x['desc'] for x in data['quality_description']}
            size = float('inf')
            ext = 'flv'
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
