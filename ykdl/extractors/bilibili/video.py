# -*- coding: utf-8 -*-

from .._common import *
from .bilibase import BiliBase, sign_api_url
from .idconvertor import av2bv


APPKEY = 'iVGUTjsxvpLeuDCf'
SECRETKEY = 'aHRmhWMLkdeMuILqORnYZocwMBpMEOdt'
api_url = 'https://interface.bilibili.com/v2/playurl'

class BiliVideo(BiliBase):
    name = '哔哩哔哩 (Bilibili)'

    def get_page_info(self):
        page_index = match1(self.url, '\?p=(\d+)', 'index_(\d+)\.') or '1'
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
                   title = '{title} - {index} - {subtitle}'.format(**vars())
               elif subtitle and subtitle != title:
                   title = '{title} - {subtitle}'.format(**vars())
               break

        return vid, title, artist

    def get_api_url(self, qn):
        params_str = urlencode([
            ('appkey', APPKEY),
            ('cid', self.vid),
            ('platform', 'html5'),
            ('player', 0),
            ('qn', qn)
        ])
        return sign_api_url(api_url, params_str, SECRETKEY)

    def prepare_list(self):
        # backup https://api.bilibili.com/x/player/pagelist?bvid=
        vid = match1(self.url, '/(av\d+|(?:BV|bv)[0-9A-Za-z]{10})')
        if vid[:2] == 'av':
            vid = av2bv(vid)
        html = get_content(self.url)
        video_list = matchall(html, '"page":(\d+),')
        if video_list:
            return ['https://www.bilibili.com/video/{}?p={}'.format(vid, p) for p in video_list]

site = BiliVideo()
