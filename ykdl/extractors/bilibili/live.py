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
        id = match1(self.url, '/(\d+)')
        data = get_response(
                'https://api.live.bilibili.com/room/v1/Room/room_init',
                params={'id': id}, cache=False).json()
        assert data['code'] == 0, data['msg']
        data = data['data']

        self.vid = data['room_id'], str(data['uid'])
        live_status = data['live_status']

        assert not data['is_locked'], '房间已封禁'
        assert not data['encrypted'], '房间已加密'
        assert live_status > 0, '主播正在觅食......'

        return live_status

    def list_only(self):
        return self.live_status() == 2

    def prepare(self):
        info = MediaInfo(self.name, True)
        room_id, uid = self.vid

        data = get_response(
                'https://api.live.bilibili.com/room/v1/Room/get_status_info_by_uids',
                params={'uids[]': uid}, cache=False).json()
        assert data['code'] == 0, data['msg']
        data = data['data'][uid]

        info.title = '{data[title]} - {data[uname]}'.format(**vars())
        info.add_comment(data['tag_name'])

        g_qn_desc = None
        aqlts = set()
        aqlts_p = set()
        size = float('inf')

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
                            self.logger.debug('skip stream: [ %s %s %s ]',
                                              stream['protocol_name'],
                                              format['format_name'],
                                              codec['codec_name'],)
                            continue
                        url_info = random.choice(codec['url_info'])
                        url = url_info['host'] + codec['base_url'] + url_info['extra']
                        info.streams[st] = {
                            'container': ext,
                            'video_profile': prf,
                            'src' : [url],
                            'size': size
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

        if self.vid is None:
            self.live_status()
        room_id, uid = self.vid
        self.start = -1  # skip is not allowed

        while True:
            data = get_response(
                    'https://api.live.bilibili.com/live/getRoundPlayVideo',
                    params={'room_id': room_id}, cache=False).json()
            assert data['code'] == 0, data['msg']
            bvid_url = data['data'].get('bvid_url')
            assert bvid_url, '轮播结束'

            info = site.parser(bvid_url)
            info.site = '哔哩哔哩轮播'
            info.title = '(轮播) ' + info.title
            yield info

site = BiliLive()
