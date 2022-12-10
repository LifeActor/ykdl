# -*- coding: utf-8 -*-

from .._common import *


class AcLive(Extractor):
    name = 'AcFun 弹幕视频网 (直播)'

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://live.acfun.cn/'
    }

    @staticmethod
    def profile_2_id(profile):
        p1, p2 = matchm(profile, '(\S+) ?(\d+M)?')
        id = {
            '蓝光': 'BD',
            '超清': 'TD',
            '高清': 'HD'
        }[p1]
        if p2:
            id += p2
        return id

    @staticmethod
    def format_mid(mid):
        mid = fullmatch(mid, '\d+')
        assert mid
        return mid

    def prepare_mid(self):
        return match1(self.url, '/live/(\d+)')

    @functools.cache
    def prepare_auth(self):
        self.mid  # scan & check
        did = 'web_{}{}{}'.format(random.randrange(1, 10),       # 9
                                  random.randrange(1, 10 ** 7),  # 9999999
                                  get_random_hex(8).upper())     # FFFFFFFF
        self.headers['Cookie'] = {'_did': did}
        data = get_response(
                'https://id.app.acfun.cn/rest/app/visitor/login',
                data=b'sid=acfun.api.visitor',
                headers=self.headers
            ).json()
        assert data['result'] == 0, data['error_msg']
        return did, data['userId'], data['acfun.api.visitor_st']

    def prepare(self):
        info = MediaInfo(self.name, True)

        did, user_id, visitor_st = self.prepare_auth()
        data = get_response(
                'https://api.kuaishouzt.com/rest/zt/live/web/startPlay',
                params={
                    'subBiz': 'mainApp',
                    'kpn': 'ACFUN_APP',
                    'kpf': 'PC_WEB',
                    'userId': user_id,
                    'did': did,
                    'acfun.api.visitor_st': visitor_st
                },
                data={
                    'authorId': self.mid,
                    'pullstreamType': 'FLV'
                },
                headers=self.headers
            ).json()
        assert data['result'] == 1, data['error_msg']
        data = data['data']

        info.title = data['caption']

        data = json.loads(data['videoPlayRes'])
        for stream in data['liveAdaptiveManifest'][0]['adaptationSet']['representation']:
            stream_profile = stream['name']
            stream_id = self.profile_2_id(stream_profile)
            info.streams[stream_id] = {
                'container': 'flv',
                'profile': stream_profile,
                'src' : [stream['url']],
                'size': Infinity
            }

        data = get_response(
                'https://live.acfun.cn/rest/pc-direct/user/userInfo',
                params={'userId': self.mid},
                headers=self.headers
            ).json()
        assert data['result'] == 0, data['error_msg']
        data = data['profile']

        info.artist = data['name']
        info.add_comment(data['signature'])

        return info

site = AcLive()
