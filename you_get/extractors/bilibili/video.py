#!/usr/bin/env python
# -*- coding: utf-8 -*-

from you_get.extractor import VideoExtractor
from you_get.util.html import get_content
from you_get.util.match import match1, matchall

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
    name = '哔哩哔哩 (Bilibili)'
    supported_stream_types = ['超清', '高清', '流畅']
    def prepare(self):

        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, 'cid=([^&]+)')
            self.title = match1(html, '<title>([^<]+)')
        for q in self.supported_stream_types:
            api_url = 'http://interface.bilibili.com/playurl?appkey=' + appkey + '&cid=' + self.vid + '&quality=' + str(3-self.supported_stream_types.index(q))
            urls, size = parse_cid_playurl(get_content(api_url))
            ext = 'flv'

            self.stream_types.append(q)
            self.streams[q] = {'container': ext, 'video_profile': q, 'src' : urls, 'size': size}

site = BiliVideo()
