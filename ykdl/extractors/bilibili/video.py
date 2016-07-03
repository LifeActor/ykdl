#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.util.html import get_content
from ykdl.util.match import match1, matchall

import hashlib
import re

appkey='f3bb208b3d081dc8'

def parse_cid_playurl(xml):
    from xml.dom.minidom import parseString
    urls = []
    size = 0
    doc = parseString(xml.encode('utf-8'))
    for durl in doc.getElementsByTagName('durl'):
        urls.append(durl.getElementsByTagName('url')[0].firstChild.nodeValue)
        size += int(durl.getElementsByTagName('size')[0].firstChild.nodeValue)
    return urls, size

class BiliVideo(VideoExtractor):
    name = u'哔哩哔哩 (Bilibili)'
    supported_stream_profile = [u'超清', u'高清', u'流畅']
    profile_2_type = {u'超清': 'TD', u'高清': 'HD', u'流畅' :'SD'}
    def prepare(self):
        info = VideoInfo(self.name)
        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, 'cid=([^&]+)')
            info.title = match1(html, '<title>([^<]+)').split("_")[0]
        assert self.vid, "can't play this video: {}".format(self.url)
        for q in self.supported_stream_profile:
            api_url = 'http://interface.bilibili.com/playurl?appkey=' + appkey + '&cid=' + self.vid + '&quality=' + str(3-self.supported_stream_profile.index(q))
            urls, size = parse_cid_playurl(get_content(api_url))
            ext = 'flv'

            info.stream_types.append(self.profile_2_type[q])
            info.streams[self.profile_2_type[q]] = {'container': ext, 'video_profile': q, 'src' : urls, 'size': size}
        return info

    def prepare_list(self):
        html = get_content(self.url)
        video_list = matchall(html, ['<option value=\'([^\']*)\''])
        return ['http://www.bilibili.com'+v for v in video_list]

site = BiliVideo()
