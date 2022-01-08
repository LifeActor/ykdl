# -*- coding: utf-8 -*-

from ..._common import *


class NeteaseMv(Extractor):
    name = 'Netease Mv (网易音乐Mv)'

    profile_type = [
        ['1080', ['1080P', 'BD']],
        [ '720', [ '超清', 'TD']],
        [ '480', [ '高清', 'HD']],
        [ '240', [ '标清', 'SD']]
    ]
    profile_2_id_profile = dict(profile_type)
    stream_ids = [id for _, id in profile_type]

    def prepare(self):
        video = MediaInfo(self.name)
        if not self.vid:
            self.vid =  match1(self.url, '\?id=(.*)', 'mv/(\d+)')

        mv = get_response('http://music.163.com/api/mv/detail/',
                          params={
                              'id': self.vid,
                              'ids': self.vid,
                              'csrf_token': ''
                          }).json()['data']

        video.title = mv['name']
        video.artist = mv['artistName']
        for id in self.stream_ids:
            if id in mv['brs']:
                stream_id, stream_profile = self.profile_2_id_profile[id]
                video.streams[stream_id] = {
                    'container': 'mp4',
                    'video_profile': stream_profile,
                    'src' : [mv['brs'][id]],
                    'size': 0
                }
        return video

site = NeteaseMv()
