#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..extractor import VideoExtractor
from ..util.html import get_content, add_header
from ..util.match import match1
from ..util import log

import json

class YinYueTai(VideoExtractor):
    name = u'YinYueTai (音乐台)'
    supported_stream_types = ['sh', 'he', 'hd', 'hc' ]
    def prepare(self):

        if not self.vid:
            self.vid = match1(self.url, 'http://\w+.yinyuetai.com/video/(\d+)')

        data = json.loads(get_content('http://ext.yinyuetai.com/main/get-h-mv-info?json=true&videoId={}'.format(self.vid)))

        assert not data['error'], 'some error happens'

        video_data = data['videoInfo']['coreVideoInfo']

        self.title = video_data['videoName']
        self.artist = video_data['artistNames']
        for s in video_data['videoUrlModels']:
            self.stream_types.append(s['qualityLevel'])
            self.streams[s['qualityLevel']] = {'container': 'flv', 'video_profile': s['qualityLevelName'], 'src' : [s['videoUrl']], 'size': s['fileSize']}

        self.stream_types = sorted(self.stream_types, key = self.supported_stream_types.index)

    def prepare_list(self):

        playlist_id = match1(self.url, 'http://\w+.yinyuetai.com/playlist/(\d+)')

        playlist_data = json.loads(get_content('http://m.yinyuetai.com/mv/get-simple-playlist-info?playlistId={}'.format(playlist_id)))

        videos = playlist_data['playlistInfo']['videos']
        # TODO
        # I should directly use playlist data instead to request by vid... to be update
        return [v['playListDetail']['videoId'] for v in videos]

site = YinYueTai()
