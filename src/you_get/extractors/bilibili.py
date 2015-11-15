#!/usr/bin/env python

from ..util.html import get_content
from ..util.match import match1, matchall
from ..embedextractor import EmbedExtractor

import re


class BiliBili(EmbedExtractor):

    def prepare(self, **kwargs):
        assert self.url

        if re.search('live', self.url):
            self.video_url.append(('biliorig', self.url))
            return

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

        if self.video_info:
            return

        vid = match1(html, 'cid=([^&]+)')

        if vid:
            self.video_info.append(('biliorig', vid))

    def download_playlist_by_url(self, url, param, **kwargs):
        self.url = url

        html = get_content(self.url)

        list = matchall(html, ['<option value=\'([^\']*)\''])

        for l in list:
            next_url = "http://www.bilibili.com{}".format(l)
            self.download(next_url, param, **kwargs)


site = BiliBili()
download = site.download
download_playlist = site.download_playlist_by_url
