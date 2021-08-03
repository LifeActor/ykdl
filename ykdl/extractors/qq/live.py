#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
import json

class QQLive(VideoExtractor):
    name = u'QQ Live (企鹅直播)'

    def prepare(self):
        info = VideoInfo(self.name, True)
        if not self.vid:
            self.vid = match1(self.url, '/(\d+)')
        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, '"room_id":(\d+)')

        #from upstream!!
        api_url = 'http://www.qie.tv/api/v1/room/{}'.format(self.vid)

        data = json.loads(get_content(api_url))
        self.logger.debug('data:\n%s', data)
        assert data['error'] == 0, 'error {}: {}'.format(data['error'], data['data'])

        livedata = data['data']
        assert livedata['show_status'] == '1', 'error: live show is not on line!!'

        info.title = livedata['room_name']
        info.artist = livedata['nickname']

        info.stream_types.append('current')
        info.streams['current'] = {
            'container': 'flv',
            'video_profile': 'current',
            'src' : ['{}/{}'.format(livedata['rtmp_url'], livedata['rtmp_live'])],
            'size': float('inf')
        }
        return info

site = QQLive()
            
