#!/usr/bin/env python

from ..extractor import VideoExtractor
from ..util.html import get_content, url_info
from ..util.match import match1, matchall

import hashlib
import re

appkey='8e9fc618fbd41e28'

def parse_cid_playurl(xml):
    from xml.dom.minidom import parseString
    try:
        doc = parseString(xml.encode('utf-8'))
        urls = [durl.getElementsByTagName('url')[0].firstChild.nodeValue for durl in doc.getElementsByTagName('durl')]
        return urls
    except:
        return []

class BiliOrig(VideoExtractor):
    name = '哔哩哔哩 (Bilibili)'
    live = False
    def prepare(self):
        assert self.url or self.vid

        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, 'cid=([^&]+)')
            self.title = match1(html, '<title>([^<]+)')

        else:
            if not self.title:
                self.title = self.name + "-" + self.vid

        assert self.vid

        if self.url:
            if re.search('live', self.url):
                self.live = True
        if not self.live:
            api_url = 'http://interface.bilibili.com/playurl?appkey=' + appkey + '&cid=' + self.vid
            urls = parse_cid_playurl(get_content(api_url))

            ext = ''
            size = 0
            for url in urls:
                _, ext, temp = url_info(url)
                size += temp
        else:
            info = get_content('http://live.bilibili.com/api/playurl?cid={}'.format(self.vid))
            urls = [matchall(info, ['CDATA\[([^\]]+)'])[1]]
            size = float('inf')
            ext = 'flv'

        self.stream_types.append('current')
        self.streams['current'] = {'container': ext, 'video_profile': 'current', 'src' : urls, 'size': size}

site = BiliOrig()
