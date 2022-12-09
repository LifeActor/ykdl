# -*- coding: utf-8 -*-

from ..._common import *


class NeteaseMv(Extractor):
    name = 'Netease MV (网易音乐 MV)'

    resolution_2_id_profile = {
        '1080': ['BD', '1080P'],
         '720': ['TD', '超清'],
         '480': ['HD', '高清'],
         '240': ['SD', '标清']
    }

    def prepare_mid(self):
        return match1(self.url, '\?id=(.*)', 'mv/(\d+)')

    def prepare(self):
        info = MediaInfo(self.name)

        data = get_response('http://music.163.com/api/mv/detail/',
                          params={
                              'id': self.mid,
                             'ids': self.mid,
                      'csrf_token': ''
                          }).json()['data']

        info.title = data['name']
        info.artist = data['artistName']
        for resolution in self.resolution_2_id_profile.keys():
            if resolution in data['brs']:
                stream_id, stream_profile = self.resolution_2_id_profile[id]
                info.streams[stream_id] = {
                    'container': 'mp4',
                    'profile': stream_profile,
                    'src': [data['brs'][id]]
                }

        return info

site = NeteaseMv()
