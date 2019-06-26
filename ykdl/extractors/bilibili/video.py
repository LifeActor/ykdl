#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1, matchall

from .bilibase import BiliBase, sign_api_url

import json

APPKEY = 'iVGUTjsxvpLeuDCf'
SECRETKEY = 'aHRmhWMLkdeMuILqORnYZocwMBpMEOdt'
api_url = 'https://interface.bilibili.com/v2/playurl'

class BiliVideo(BiliBase):
    name = u'哔哩哔哩 (Bilibili)'

    def get_page_info(self):
        av_id = match1(self.url, '(?:/av|aid=)(\d+)')
        page_index = '1'
        if "#page=" in self.url or "?p=" in self.url or 'index_' in self.url:
            page_index = match1(self.url, '(?:#page|\?p)=(\d+)', 'index_(\d+)\.')
        if page_index == '1':
            self.url = 'https://www.bilibili.com/av{}/'.format(av_id)
        else:
            self.url = 'https://www.bilibili.com/av{}/?p={}'.format(av_id, page_index)

        html = get_content(self.url)
        date = json.loads(match1(html, '__INITIAL_STATE__=({.+?});'))['videoData']
        title = date['title']
        artist = date['owner']['name']
        pages = date['pages']
        for page in pages:
           index = str(page['page'])
           subtitle = page['part']
           if index == page_index:
               vid = page['cid']
               if len(pages) > 1:
                   title = u'{} - {} - {}'.format(title, index, subtitle)
               elif subtitle and subtitle != title:
                   title = u'{} - {}'.format(title, subtitle)
               break

        return vid, title, artist

    def get_api_url(self, qn):
        params_str = 'appkey={}&cid={}&player=0&qn={}'.format(APPKEY, self.vid, qn)
        return sign_api_url(api_url, params_str, SECRETKEY)

    def prepare_list(self):
        av_id = match1(self.url, '(?:/av|aid=)(\d+)')
        self.url = 'https://www.bilibili.com/av{}/'.format(av_id)
        html = get_content(self.url)
        video_list = matchall(html, ['"page":(\d+),'])
        if video_list:
            return ['https://www.bilibili.com/av{}/?p={}'.format(av_id, p) for p in video_list]

site = BiliVideo()
