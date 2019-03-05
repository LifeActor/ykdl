#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content, add_header
from ykdl.util.match import match1, matchall
from ykdl.util.jsengine import JSEngine, javascript_is_supported
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.compact import urlencode

import time
import json
import uuid


douyu_match_pattern = [ 'class="hroom_id" value="([^"]+)',
                        'data-room_id="([^"]+)'
                      ]
class Douyutv(VideoExtractor):
    name = u'斗鱼直播 (DouyuTV)'

    stream_ids = ['BD10M', 'BD8M', 'BD4M', 'BD', 'TD', 'HD', 'SD']
    profile_2_id = {
        u'蓝光10M': 'BD10M',
        u'蓝光8M': 'BD8M',
        u'蓝光4M': 'BD4M',
        u'蓝光': 'BD',
        u'超清': 'TD',
        u'高清': 'HD',
        u'流畅': 'SD'
     }

    def prepare(self):
        assert javascript_is_supported, "No JS Interpreter found, can't parse douyu live!"

        info = VideoInfo(self.name, True)
        add_header("Referer", 'https://www.douyu.com')

        title = None
        artist = None
        self.vid = match1(self.url, 'douyu.com/(\d+)')

        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, 'room_id\s*=\s*(\d+);', '"room_id.?":(\d+)', 'data-onlineid=(\d+)')
            title = match1(html, 'Title-headlineH2">([^<]+)<')
            artist = match1(html, 'Title-anchorName" title="([^"]+)"')

        if not artist:
            html_content = get_content('https://open.douyucdn.cn/api/RoomApi/room/' + self.vid)
            data = json.loads(html_content)
            if data['error'] == 0:
                title = data['data']['room_name']
                artist = data['data']['owner_name']

        info.title = u'{} - {}'.format(title, artist)
        info.artist = artist

        html_content = get_content('https://www.douyu.com/swf_api/homeH5Enc?rids=' + self.vid)
        data = json.loads(html_content)
        assert data['error'] == 0, data['msg']
        js_enc = data['data']['room' + self.vid]

        try:
            # try load local .js file first
            # from https://cdnjs.com/libraries/crypto-js
            from pkgutil import get_data
            js_md5 = get_data(__name__, 'crypto-js-md5.min.js')
            if isinstance(js_md5, bytes):
                js_md5 = js_md5.decode()
        except IOError:
            js_md5 = get_content('https://cdnjs.cloudflare.com/ajax/libs/crypto-js/3.1.9-1/crypto-js.min.js')

        js_ctx = JSEngine(js_md5)
        js_ctx.eval(js_enc)
        did = uuid.uuid4().hex
        tt = str(int(time.time()))
        ub98484234 = js_ctx.call('ub98484234', self.vid, did, tt)
        self.logger.debug('ub98484234: ' + ub98484234)
        params = {
            'v': match1(ub98484234, 'v=(\d+)'),
            'did': did,
            'tt': tt,
            'sign': match1(ub98484234, 'sign=(\w{32})'),
            'cdn': '',
            'iar': 0,
            'ive': 0
        }

        def get_live_info(rate=0):
            params['rate'] = rate
            data = urlencode(params)
            if not isinstance(data, bytes):
                data = data.encode()
            html_content = get_content('https://www.douyu.com/lapi/live/getH5Play/{}'.format(self.vid), data=data)
            self.logger.debug(html_content)

            live_data = json.loads(html_content)
            if live_data['error']:
                return live_data['msg']

            live_data = live_data["data"]
            real_url = '{}/{}'.format(live_data['rtmp_url'], live_data['rtmp_live'])
            rate_2_profile = dict((rate['rate'], rate['name']) for rate in live_data['multirates'])
            video_profile = rate_2_profile[live_data['rate']]
            stream = self.profile_2_id[video_profile]
            if stream in info.streams:
                return
            info.stream_types.append(stream)
            info.streams[stream] = {
                'container': 'flv',
                'video_profile': video_profile,
                'src' : [real_url],
                'size': float('inf')
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
        assert len(info.stream_types), error_msg
        info.stream_types = sorted(info.stream_types, key=self.stream_ids.index)
        return info

    def prepare_list(self):

        html = get_content(self.url)
        return matchall(html, douyu_match_pattern)

site = Douyutv()
