#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1, matchall
from ykdl.compact import compact_bytes

import hashlib
import json
import time

from .bilibase import BiliBase

appkey='f3bb208b3d081dc8'
SECRETKEY_MINILOADER = '1c15888dc316e05a15fdd0a02ed6584f'

class BiliVideo(BiliBase):
    name = u'哔哩哔哩 (Bilibili)'

    def get_vid_title(self):
        if "#page=" in self.url:
            page_index = match1(self.url, '#page=(\d+)')
            av_id = match1(self.url, '\/(av\d+)')
            self.url = 'http://www.bilibili.com/{}/index_{}.html'.format(av_id, page_index)
        if not self.vid:
            html = get_content(self.url)
            vid = match1(html, 'cid=(\d+)', 'cid=\"(\d+)', '\"cid\":(\d+)')
            title = match1(html, '<h1 title="([^"]+)', '<title>([^<]+)').strip()

        return vid, title

    def get_api_url(self, q):
        t = int(time.time())
        sign_this = hashlib.md5(compact_bytes('cid={}&player=1&quality={}&ts={}{}'.format(self.vid, q, t, SECRETKEY_MINILOADER), 'utf-8')).hexdigest()
        return 'http://interface.bilibili.com/playurl?cid={}&player=1&quality={}&ts={}&sign={}'.format(self.vid, q, t, sign_this)

    def prepare_list(self):
        html = get_content(self.url)
        video_list = matchall(html, ['<option value=\'([^\']*)\''])
        if video_list:
            return ['http://www.bilibili.com'+v for v in video_list]

site = BiliVideo()
