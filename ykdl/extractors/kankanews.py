#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.util.html import get_content
from ykdl.util.match import match1, matchall

class KankanNews(VideoExtractor):
    name = u'看看新闻 (kankannews)'

    def prepare(self):
        info = VideoInfo(self.name)
        id1 = match1(self.url, 'a/([^\.]+)\.')
        api1 = 'http://www.kankanews.com/vxml/{}.xml'.format(id1)
        video_data1 = get_content(api1)
        info.title = match1(video_data1, '<title>([^<]+)<')
        self.vid = match1(video_data1, '<omsid>([^<]+)<')
        assert self.vid != '0', self.url + u": Not a video news link!"
        api2 = 'http://v.kankanews.com/index.php?app=api&mod=public&act=getvideo&id={}'.format(self.vid)
        video_data2 = get_content(api2)
        urls = matchall(video_data2, ['<videourl><!\[CDATA\[([^\]]+)'])
        info.stream_types.append('current')
        info.streams['current'] = {'container': 'mp4', 'video_profile': 'current', 'src' : urls, 'size': 0}
        return info

site = KankanNews()
