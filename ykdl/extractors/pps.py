#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from ykdl.util.match import match1
from ykdl.util.html import get_content, add_header
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.compact import urlencode
import time

class PPS(VideoExtractor):

    name = u"奇秀（Qixiu)"

    def prepare(self):

        info = VideoInfo(self.name)
        if self.url:
            self.vid = match1(self.url, r'/room/(\d+)')
            
        # Get title and anchor id
        url = 'https://m-x.pps.tv/room/' + self.vid
        ua = 'Mozilla/5.0 (iPad; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.0 Mobile/15E148 Safari/604.1'
        add_header('Referer', url)
        add_header('User-Agent', ua)
        info.extra['ua'] = ua
        info.extra['referer'] = url
        html = get_content(url)
        anchor_id = match1(html, r'"anchor_id":"(.+?)"')
        info.title = match1(html, r'"nick_name":"(.+?)"')

        # Get IP from iqiyi's server
        tm = int(time.time())
        api_url = 'http://data.video.qiyi.com/v.mp4?_={}&callback=jsonCallBack'.format(tm)
        html = get_content(api_url)
        ip = match1(html, r'-(\d+\.\d+\.\d+\.\d+)')

        # Get stream url
        tm = int(time.time())
        params = {
            'qd_tm': tm,
            'typeId': 1,
            'platform': 7,
            'vid': 0,
            'qd_vip': 0,
            'qd_uid': anchor_id,
            'qd_ip': ip,
            'qd_vipres': 0,
            'qd_src': 'h5_xiu',
            'qd_tvid': 0,
            '_': tm,
            'callback': 'jsonCallBack'
        }
        api_url = 'http://api-live.iqiyi.com/stream/geth5?' + urlencode(params)
        html = get_content(api_url)
        data = json.loads(html[13:-1])
        url = data['data']['hls']
        info.stream_types.append('current')
        info.streams['current'] = {'video_profile': 'current', 'container': 'm3u8', 'src': [url], 'size' : 0}
        return info

site = PPS()
