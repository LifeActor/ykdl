#!/usr/bin/env python

from ..common import *
from ..extractor import VideoExtractor
from ..embedextractor import EmbedExtractor

import hashlib
import re

# API key provided by cnbeining
appkey='85eb6835b0a1034e';
secretkey = '2ad42749773c441109bdc0191257a664'

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
    def prepare(self, **kwargs):
        assert self.url or self.vid

        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, 'cid=([^&]+)')
            self.title = match1(html, '<title>([^<]+)')

        else:
            if 'title' in kwargs and kwargs['title']:
                self.title = kwargs['title']
            else:
                self.title = self.name + "-" + self.vid

        assert self.vid

        if self.url:
            if re.search('live', self.url):
                self.live = True
        if not self.live:
            sign_this = hashlib.md5(bytes('appkey=' + appkey + '&cid=' + self.vid + secretkey, 'utf-8')).hexdigest()
            api_url = 'http://interface.bilibili.com/playurl?appkey=' + appkey + '&cid=' + self.vid + '&sign=' + sign_this
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

class BiliEmbed(EmbedExtractor):

    def prepare(self, **kwargs):
        assert self.url

        html = get_content(self.url)
        self.title = match1(html, '<title>([^<]+)')
        vid = match1(html, '&vid=([^\"]+)')
        if vid:
            self.video_info.append(('letv', vid))

        vid = match1(html, '&video_id=([^\"]+)')

        if vid:
            self.video_info.append(('hunantv', vid))

        vid = match1(html, '&ykid=([^\"]+)')

        if vid:
            self.video_info.append(('youku', vid))

class BiliBili():

    def __init__(self, *args):
        self.orig = BiliOrig()
        self.embed = BiliEmbed()
        if args:
            self.url = args[0]

    def download_by_url(self, url, param, **kwargs):
        self.url = url

        html = get_content(self.url)
        self.title = match1(html, '<title>([^<]+)')
        vids = matchall(html, ['cid=([^&]+)'])

        if vids:
            self.orig.download_by_url(self.url, param, title=self.title, **kwargs)
        else:
            self.embed.download(self.url, param, **kwargs)

    def download_playlist_by_url(self, url, param, **kwargs):
        self.url = url

        html = get_content(self.url)

        list = matchall(html, ['<option value=\'([^\']*)\''])

        for l in list:
            next_url = "http://www.bilibili.com{}".format(l)
            self.download_by_url(next_url, param, **kwargs)


site = BiliBili()
download = site.download_by_url
download_playlist = site.download_playlist_by_url
