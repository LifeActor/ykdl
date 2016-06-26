#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1
from ykdl.extractor import VideoExtractor

import json

class QQLive(VideoExtractor):
    name = u'QQ Live (企鹅直播)'

    mutli_bitrate = ['middle2', 'middle']

    bitrate_2_type = {'middle2': 'HD', 'middle': 'SD'}

    bitrate_2_profile = {'middle2': u'高清', 'middle': u'标清'}

    def prepare(self):
        self.live = True
        if not self.vid:
            self.vid = match1(self.url, '/(\d+)')
        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, '"room_id":(\d+)')

        #from upstream!!
        api_url = 'http://www.qie.tv/api/v1/room/{}'.format(self.vid)

        metadata = json.loads(get_content(api_url))
        assert metadata['error'] == 0, 'error {}: {}'.format(metadata['error'], metadata['data'])

        livedata = metadata['data']
        assert livedata['show_status'] == '1', 'error: live show is not on line!!'

        self.title = livedata['room_name']
        self.artist = livedata['nickname']

        base_url = livedata['rtmp_url']

        if 'hls_url' in livedata:
            self.stream_types.append('BD')
            self.streams['BD'] = {'container': 'm3u8', 'video_profile': u'原画', 'src' : [livedata['hls_url']], 'size': float('inf')}

        mutli_stream = livedata['rtmp_multi_bitrate']
        for i in self.mutli_bitrate:
            if i in mutli_stream:
                self.stream_types.append(self.bitrate_2_type[i])
                self.streams[self.bitrate_2_type[i]] = {'container': 'flv', 'video_profile': self.bitrate_2_profile[i], 'src' : [base_url + '/' + mutli_stream[i]], 'size': float('inf')}

site = QQLive()
            
