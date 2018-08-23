#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.util.html import get_content, add_header
from ykdl.util.match import match1, matchall

class HuyaLive(VideoExtractor):
    name = u"Huya Live (虎牙直播)"

    def prepare(self):
        info = VideoInfo(self.name)

        html  = get_content(self.url)

        channel = match1(html, '"channel":"*(\d+)"*,')
        sid = match1(html, '"sid":"(\d+)",', '"sid":(\d+),')
        assert not channel == '0' and not sid == '0', "live video is offline"


        _hex = '0000009E10032C3C4C56066C6976657569660D6765744C6976696E67496E666F7D0000750800010604745265711D0000680A0A0300000000000000001620FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF2600361777656226323031377633322E313131302E33266875796146005C0B1300000000{}2300000000{}3300000000000000000B8C980CA80C'
        hex_content = _hex.format( format(int(channel), 'X').zfill(8), format(int(sid), 'X').zfill(8) )
        video_data = get_content('http://cdn.wup.huya.com/', data = bytearray.fromhex(hex_content), charset = 'ignore').decode("utf-8",  errors='ignore')
        assert channel in video_data, "live video is offline"

        vid = match1(video_data, '(%s-%s[^f]+)'%(channel, sid))

        wsSecret = match1(video_data, 'wsSecret=([0-9a-z]{32})')
        wsTime = match1(video_data , 'wsTime=([0-9a-z]{8})')
        line = match1(video_data, '://(.+\.(flv|stream)\.huya\.com/(hqlive|huyalive))')
        flv_url = 'http://{}/{}.flv?wsSecret={}&wsTime={}'.format(line, vid, wsSecret, wsTime)
        info.stream_types.append("current")
        info.streams["current"] = {'container': 'mp4', 'video_profile': "current", 'src': [flv_url], 'size' : float('inf')}
        return info

site = HuyaLive()
