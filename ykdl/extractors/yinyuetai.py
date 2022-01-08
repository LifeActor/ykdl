# -*- coding: utf-8 -*-

from ._common import *


class YinYueTai(Extractor):
    name = 'YinYueTai (音乐台)'

    types_2_id_profile = {
        'sh': ['BD', '原画'],
        'he': ['TD', '超清'],
        'hd': ['HD', '高清'],
        'hc': ['SD', '标清']
    }

    def prepare(self):
        info = MediaInfo(self.name)
        if not self.vid:
            self.vid = match1(self.url,
                              '//\w+.yinyuetai.com/video/(?:h5/)?(\d+)')

        data = get_response('http://ext.yinyuetai.com/main/get-h-mv-info',
                            params={
                                'json': 'true',
                                'videoId': self.vid
                            }).json()
        assert not data['error'], 'some error happens'

        video_data = data['videoInfo']['coreVideoInfo']
        info.title = video_data['videoName']
        info.artist = video_data['artistNames']

        for s in video_data['videoUrlModels']:
            stream_id, video_profile = self.types_2_id_profile[s['qualityLevel']]
            info.streams[stream_id] = {
                'container': 'flv',
                'video_profile': video_profile,
                'src' : [s['videoUrl']],
                'size': s['fileSize']
            }

        return info

    def prepare_list(self):
        playlist_id = match1(self.url, 'http://\w+.yinyuetai.com/playlist/(\d+)')
        playlist_data = get_response(
                'http://m.yinyuetai.com/mv/get-simple-playlist-info'
                params={'playlistId': playlist_id}).json()

        videos = playlist_data['playlistInfo']['videos']
        # TODO
        # I should directly use playlist data instead to request by vid...
        # to be update
        return [v['playListDetail']['videoId'] for v in videos]

site = YinYueTai()
