#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.compact import unescape
import json
import time


class QQEGame(VideoExtractor):
    name = u'QQ EGAME (企鹅电竟)'

    mutli_bitrate = ['0', '4000', '1500', '900']

    bitrate_2_type = {'0': 'Souce', '4000': 'BD', '1500': 'HD', '900': 'SD'}

    bitrate_2_profile = {'0': u'原画', '4000': u'蓝光', '1500': u'高清', '900': u'流畅'}

    def prepare(self):
        info = VideoInfo(self.name, True)
        html = get_content(self.url)
        if not self.vid:
            self.vid = match1(self.url, '/(\d+)')
        if not self.vid:
            self.vid = match1(html, '"liveAddr":"([0-9\_]+)"')
        self.pid = self.vid

        # from upstream!!
        mobileHtml = get_content('https://m.egame.qq.com/live?anchorid={}'.format(self.vid))
        assert match1(mobileHtml,'"isLive":(\d+)') == '1', 'error: live show is not on line!!'

        info.title = match1(html, 'title:"([^"]*)"')
        info.artist = match1(html, 'nickName:"([^"]+)"')

        for data in json.loads(match1(html, '"urlArray":(\[[^\]]+\])')):
            info.stream_types.append(self.bitrate_2_type[data["bitrate"]])
            info.streams[self.bitrate_2_type[data["bitrate"]]] = {'container': 'flv', 'video_profile': data["desc"], 'src': ["%s&_t=%s000"%(unescape(data["playUrl"]),int(time.time()))], 'size': float('inf')}

        return info

site = QQEGame()
