#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1, matchall
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from xml.dom.minidom import parseString

class Taobao(VideoExtractor):
    name = u'Taobao (淘宝)'

    stream_2_id = { 'ud': 'BD', 'hd': 'TD', 'sd': 'HD', 'ld': 'SD' }

    stream_ids = ['TD', 'HD', 'SD', 'BD']

    def prepare(self):
        info = VideoInfo(self.name)

        html = get_content(self.url)
        self.vid = match1(html, "(\d+)\.swf")

        xml = get_content("http://cloud.video.taobao.com/videoapi/info.php?vid={}".format(self.vid))

        doc = parseString(xml)
        videos = doc.getElementsByTagName("videos")[0]

        n = 0
        for video in videos.getElementsByTagName('video'):
            if not n % 2:
                lenth = video.getElementsByTagName('length')[0].firstChild.nodeValue
                url = video.getElementsByTagName('video_url')[0].firstChild.nodeValue
                profile = self.stream_2_id[video.getElementsByTagName('type')[0].firstChild.nodeValue]
                info.stream_types.append(profile)
                info.streams[profile] = {'container': 'flv', 'video_profile': profile, 'src' : [url+'/start_0/end_{}/1.flv'.format(lenth)], 'size': int(lenth)}

        info.stream_types = sorted(info.stream_types, key = self.stream_ids.index)
        return info

        

site = Taobao()
