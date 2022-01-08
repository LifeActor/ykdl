# -*- coding: utf-8 -*-

from .._common import *


class QQLive(Extractor):
    name = 'QQ Live (企鹅直播)'

    def prepare(self):
        info = MediaInfo(self.name, True)
        if not self.vid:
            self.vid = match1(self.url, '/(\d+)')
        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, '"room_id":(\d+)')

        #from upstream!!
        data = get_response('http://www.qie.tv/api/v1/room/' + self.vid).json()
        assert data['error'] == 0, 'error {}: {}'.format(data['error'], data['data'])

        livedata = data['data']
        assert livedata['show_status'] == '1', 'error: live show is not on line!!'

        info.title = livedata['room_name']
        info.artist = livedata['nickname']

        info.streams['current'] = {
            'container': 'flv',
            'video_profile': 'current',
            'src' : ['{}/{}'.format(livedata['rtmp_url'], livedata['rtmp_live'])],
            'size': float('inf')
        }
        return info

site = QQLive()
            
