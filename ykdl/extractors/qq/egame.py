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
    
    lv_2_id = {
        10: 'BD10M',
         8: 'BD8M',
         6: 'BD6M',
         4: 'BD4M',
         3: 'TD',
         2: 'HD',
         1: 'SD',
    }

    def prepare(self):
        info = VideoInfo(self.name, True)
        if not self.vid:
            self.vid = match1(self.url, '/(\d+)')
        if not self.url:
            self.url = 'https://egame.qq.com/' + self.vid
        html = get_content(self.url)

        title = match1(html, 'title:"([^"]*)"')
        info.artist = artist = match1(html, 'nickName:"([^"]+)"')
        info.title = u'{} - {}'.format(title, artist)

        playerInfo = match1(html, 'playerInfo = ({.+?});')
        self.logger.debug("playerInfo => %s" % (playerInfo))

        assert playerInfo, 'error: live show is not on line!!'
        playerInfo = json.loads(playerInfo)

        for u in playerInfo['urlArray']:
            stream = self.lv_2_id[u['levelType']]
            info.stream_types.append(stream)
            info.streams[stream] = {
                'container': 'flv',
                'video_profile': u['desc'],
                'src': [u['playUrl']],
                'size': float('inf')
            }

        info.stream_types = sorted(info.stream_types, key=self.stream_ids.index)
        return info

site = QQEGame()
