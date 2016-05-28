#!/usr/bin/env python
# -*- coding: utf-8 -*-

from you_get.extractor import VideoExtractor
from you_get.util.html import get_content, add_header
from you_get.util.match import match1, matchall

import hashlib
import re
import json
appkey='8e9fc618fbd41e28'

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
        page = 1
        if not self.vid:
            self.vid = match1(self.url, 'av(\d+)')
            page = match1(self.url, 'page=(\d+)', '_(\d+).html') or 1
            html = get_content(self.url)

            self.title = match1(html, '<title>([^<]+)')

        api_url = 'http://www.bilibili.com/m/html5?aid={}&page={}'.format(self.vid,page)
        json_data = json.loads(get_content(api_url))
        urls = [json_data['src']]
        ext = 'flv'
        self.stream_types.append('current')
        self.streams['current'] = {'container': ext, 'video_profile': 'current', 'src' : urls, 'size': 0}

site = BiliVideo()
