# -*- coding: utf-8 -*-

from .._common import *
from .. import _byted


class IXiGua(Extractor):
    name = '西瓜直播 (IXiGua)'

    quality_2_profile_id = {
          'ORIGIN': ['原画', 'OG'],
        'FULL_HD1': ['蓝光', 'BD'],
             'HD1': ['超清', 'TD'],
             'SD2': ['高清', 'HD'],
          'REVIEW': ['流畅', 'SD'],
     }

    def prepare(self):
        info = MediaInfo(self.name)

        html = _byted.get_content(self.url)
        data = match1(html, 'id="SSR_HYDRATED_DATA">(.+?)</script>')
        self.logger.debug('data: \n%s', data)
        data = json.loads(data)

        room_info = data['roomData']
        assert room_info['status'] == 2, 'live is off!!!'

        title = room_info['title']
        info.artist = artist = room_info['anchorInfo']['name']
        info.title = '{title} - {artist}'.format(**vars())

        for v in room_info['playInfo']:
            video_profile, stream = self.quality_2_profile_id[v['Resolution']]
            if 'FlvUrl' in v:
                info.streams[stream + '-' + 'flv'] = {
                    'container': 'flv',
                    'video_profile': video_profile,
                    'src' : [v['FlvUrl']],
                }
            if 'HlsUrl' in v:
                info.streams[stream + '-' + 'm3u'] = {
                    'container': 'm3u8',
                    'video_profile': video_profile,
                    'src' : [v['HlsUrl']],
                }

        return info

site = IXiGua()
