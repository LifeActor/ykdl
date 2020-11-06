#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
import json


class QQEGame(VideoExtractor):
    name = u'QQ EGAME (企鹅电竟)'

    stream_ids = ['BD10M', 'BD8M', 'BD6M', 'BD4M', 'BD', 'TD', 'HD', 'SD']

    profile_2_id = {
        u'蓝光10M': 'BD10M',
        u'蓝光8M': 'BD8M',
        u'蓝光6M': 'BD6M',
        u'蓝光4M': 'BD4M',
        u'蓝光': 'BD',
        u'超清': 'TD',
        u'高清': 'HD',
        u'流畅': 'SD',
    }

    def parse_unicode(self, s):
        return json.loads('["{}"]'.format(s))[0]

    def prepare(self):
        info = VideoInfo(self.name, True)
        if not self.vid:
            self.vid = match1(self.url, '/(\d+)')
        html = get_content('https://m.egame.qq.com/live?anchorid=' + self.vid)

        title = self.parse_unicode(match1(html, '"title":"([^"\{\}]*)"'))
        info.artist = artist = self.parse_unicode(match1(html, '"nickName":"([^"]+)"'))
        info.title = u'{} - {}'.format(title, artist)

        assert match1(html, 'isLive":(\d+)') == '1', 'error: live show is not on line!!'

        html = get_content(self.url)
        urlArray = json.loads(match1(html, '"urlArray":(\[[^\]]+\])'))
        self.logger.debug("urlArray => {}".format(urlArray))

        for u in urlArray:
            video_profile = u['desc']
            stream = self.profile_2_id[video_profile]
            info.stream_types.append(stream)
            info.streams[stream] = {
                'container': 'flv',
                'video_profile': video_profile,
                'src': [u['playUrl']],
                'size': float('inf')
            }

        info.stream_types = sorted(info.stream_types, key=self.stream_ids.index)
        return info


site = QQEGame()
