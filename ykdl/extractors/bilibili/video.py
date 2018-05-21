#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1, matchall

from .bilibase import BiliBase, sign_api_url


SECRETKEY = '1c15888dc316e05a15fdd0a02ed6584f'
api_url = 'https://interface.bilibili.com/v2/playurl'

class BiliVideo(BiliBase):
    name = u'哔哩哔哩 (Bilibili)'

    def get_vid_title(self):
        if "#page=" in self.url or "?p=" in self.url:
            page_index = match1(self.url, '(?:#page|\?p)=(\d+)')
            av_id = match1(self.url, '/av(\d+)')
            self.url = 'https://www.bilibili.com/av{}/index_{}.html'.format(av_id, page_index)
        if "aid=" in self.url:
            av_id = match1(self.url, 'aid=(\d+)')
            self.url = 'https://www.bilibili.com/video/av' + av_id
        if not self.vid:
            html = get_content(self.url)
            vid = match1(html, 'cid(?==|")=?"?:?(\d+)')
            title = match1(html, '<h1 title="([^"]+)', '<title>([^<]+)').strip()

        return vid, title

    def get_api_url(self, qn):
        params_str = 'cid={}&player=1&qn={}'.format(self.vid, qn)
        return sign_api_url(api_url, params_str, SECRETKEY)

    def prepare_list(self):
        av_id = match1(self.url, '(?:/av|aid=)(\d+)')
        if "aid=" in self.url:
            self.url = 'https://www.bilibili.com/video/av' + av_id
        html = get_content(self.url)
        video_list = matchall(html, ['"page":(\d+),'])
        if video_list:
            return ['https://www.bilibili.com/av{}/index_{}.html'.format(av_id, p) for p in video_list]

site = BiliVideo()
