#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import datetime
import platform


from ykdl.util.html import get_content, url_info
from ykdl.util.match import match1, matchall
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo


class LeLiveFi(VideoExtractor):
    name = u"Le Live Finance(乐视财经)"

    supported_stream_types = ['flv_1080p3m', 'flv_1080p', 'flv_1300', 'flv_1000', 'flv_720p', 'flv_350']

    stream_2_profile = {'flv_1080p3m': u'1080p' ,'flv_1080p': u'1080p' , 'flv_1300': u'超清', 'flv_1000': u'高清' , 'flv_720p': u'标清', 'flv_350': u'流畅' }

    stream_2_id = {'flv_1080p3m': 'BD', 'flv_1080p': 'BD' , 'flv_1300': 'TD', 'flv_1000': 'HD' , 'flv_720p': 'SD', 'flv_350': 'LD' }

    stream_ids = ['BD', 'TD', 'HD', 'SD', 'LD']

    def prepare(self):
        info = VideoInfo(self.name, True)
        html = get_content(self.url)
        self.vid = match1(html, 'liveId\s*:\s*"(\d+)"') or match1(self.url, 'd=(\d+)', 'live/(\d+)')

        live_data = json.loads(get_content('http://player.pc.le.com/player/startup_by_pid/1001/{}?host=live.le.com'.format(self.vid)))
        assert 'status' in live_data and live_data['status'] == 2, "Live show is finished, playback is not supported!"
        info.title = live_data['title']

        stream_data = live_data['rows']

        for s in stream_data:
            stream_id = self.stream_2_id[s['rateType']]
            stream_profile = self.stream_2_profile[s['rateType']]
            if not stream_id in info.stream_types:
                info.stream_types.append(stream_id)
                streamUrl = s['streamUrl'] + '&format=1&expect=2&termid=1&platid=10&playid=1&sign=live_web&splatid=1001&vkit=20161017&station={}'.format( self.vid)
                data = json.loads(get_content(streamUrl))
                src = data['location']
                info.streams[stream_id] = {'container': 'm3u8', 'video_profile': stream_profile, 'size' : float('inf'), 'src' : [src]}
        info.stream_types = sorted(info.stream_types, key = self.stream_ids.index)
        return info

site = LeLiveFi()
