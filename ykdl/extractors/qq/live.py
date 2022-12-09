# -*- coding: utf-8 -*-

from .._common import *


class QQLive(Extractor):
    name = 'QQ Live (企鹅直播)'

    def prepare_mid(self):
        mid = match1(self.url, '/(\d+)')
        if mid is None:
            html = get_content(self.url)
            mid = match1(html, '"room_id":(\d+)')
        return mid

    def prepare(self):
        info = MediaInfo(self.name, True)

        #from upstream!!
        data = get_response(
            'http://www.qie.tv/api/v1/room/{self.mid}'.format(**vars())).json()
        assert data['error'] == 0, '{error}: {data}'.format(**data)

        livedata = data['data']
        assert livedata['show_status'] == '1', 'live is offline!!'

        info.title = livedata['room_name']
        info.artist = livedata['nickname']

        info.streams['current'] = {
            'container': 'flv',
            'profile': 'current',
            'src' : ['{rtmp_url}/{rtmp_live}'.format(**livedata)],
            'size': Infinity
        }
        return info

site = QQLive()
            
