# -*- coding: utf-8 -*-

from .._common import *


class BiliLive(Extractor):
    name = 'Bilibili live (哔哩哔哩直播)'

    profile_2_id = {
        '杜比': 'unknown',  # FIXME: placeholder
          '4K': '4K',
        '原画': 'OG',
        '蓝光': 'BD',
        '超清': 'TD',
        '高清': 'HD',
        '流畅': 'SD'
    }

    def live_status(self):
        mid = self.mid[0]
        data = get_response(
                'https://api.live.bilibili.com/room/v1/Room/room_init',
                params={'id': mid}, cache=False).json()
        assert data['code'] == 0, data['msg']
        data = data['data']

        self.mid = mid, data['room_id'], str(data['uid'])
        live_status = data['live_status']

        assert not data['is_locked'], '房间已封禁'
        assert not data['encrypted'], '房间已加密'
        assert live_status > 0, '主播正在觅食......'

        return live_status

    def list_only(self):
        return self.live_status() == 2

    @staticmethod
    def format_mid(mid):
        # [0]:  web room id
        # [1]: real room id
        # [2]:      user id
        if not isinstance(mid, tuple):
            mid = (mid, )
        wrid = fullmatch(mid[0], '\d+')
        assert wrid
        return wrid, *mid[1:]

    def prepare_mid(self):
        return match1(self.url, '/(\d+)')

    def prepare(self):
        info = MediaInfo(self.name, True)

        _, room_id, uid = self.mid
        data = get_response(
                'https://api.live.bilibili.com/room/v1/Room/get_status_info_by_uids',
                params={'uids[]': uid}, cache=False).json()
        assert data['code'] == 0, data['msg']
        data = data['data'][uid]

        info.title = '{title} - {uname}'.format(**data)
        info.artist = data['uname']
        info.add_comment(data['tag_name'])

        g_qn_desc = None
        aqlts = set()
        aqlts_p = set()

        def get_live_info(qn=1):
            data = get_response(
                    'https://api.live.bilibili.com/xlive/web-room/v2/index/getRoomPlayInfo',
                    params={
                        'room_id': room_id,
                        'protocol': '0,1',    # 0 = http_stream, 1 = http_hls
                        'format': '0,1,2',
                        'codec': '0,1',       # 0 = avc, 1 = hevc
                        'qn': qn,
                        'platform': 'web',
                        'ptype': 8,
                        'dolby': 5
                    }, cache=False).json()
            assert data['code'] == 0, data['msg']
            data = data['data']['playurl_info']['playurl']

            nonlocal g_qn_desc, aqlts
            if g_qn_desc is None:
                g_qn_desc = {x['qn']: x['desc'] for x in data['g_qn_desc']}
            qlt = None

            for stream in data['stream']:
                for format in stream['format']:
                    for codec in format['codec']:
                        aqlts.update(x for x in codec['accept_qn']
                                     if x not in aqlts_p)
                        if qlt is None:
                            qlt = codec['current_qn']
                            prf = g_qn_desc[qlt]
                        st = self.profile_2_id[prf]
                        if 'http_hls' in stream['protocol_name']:
                            ext = 'm3u8'
                            st += '-hls'
                        else:
                            ext = format['format_name']
                        if codec['codec_name'] == 'hevc':
                            st += '-h265'
                        if st in info.streams:
                            st += '-bak'
                        #    self.logger.debug('skip stream: [ %s %s %s ]',
                        #                      stream['protocol_name'],
                        #                      format['format_name'],
                        #                      codec['codec_name'],)
                        #    continue
                        url_info = random.choice(codec['url_info'])
                        url = url_info['host'] + codec['base_url'] + url_info['extra']
                        info.streams[st] = {
                            'container': ext,
                            'profile': prf,
                            'src' : [url],
                            'size': Infinity
                        }

            if qn == 1:
                aqlts.remove(qlt)
                aqlts_p.add(qlt)
                while aqlts:
                    qlt = aqlts.pop()
                    aqlts_p.add(qlt)
                    get_live_info(qlt)

        get_live_info()
        info.extra.referer= 'https://live.bilibili.com/'
        return info

    def prepare_list(self):
        from .video import site

        try:
            room_id = self.mid[1]
        except IndexError:
            self.live_status()
            room_id = self.mid[1]
        self.start = -1  # skip is not allowed
        self.end = 0     # never show index

        bvid_url_last = None
        repeat_times = 0
        stop_threshold = 2
        while True:
            data = get_response(
                    'https://api.live.bilibili.com/live/getRoundPlayVideo',
                    params={'room_id': room_id}, cache=False).json()
            assert data['code'] == 0, data['msg']
            bvid_url = data['data'].get('bvid_url')
            assert bvid_url, '轮播结束'

            if bvid_url == bvid_url_last:
                repeat_times += 1
                assert repeat_times < stop_threshold, 'repeat'
            else:
                bvid_url_last = bvid_url
                repeat_times = 0

            info = site.parser(bvid_url)
            info.site = '哔哩哔哩轮播'
            info.title = '(轮播) ' + info.title
            yield info

site = BiliLive()
