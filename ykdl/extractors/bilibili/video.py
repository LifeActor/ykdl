# -*- coding: utf-8 -*-

from .._common import *
from .util import *
from .bilibase import BiliBase


APPKEY = 'iVGUTjsxvpLeuDCf'
SECRETKEY = 'aHRmhWMLkdeMuILqORnYZocwMBpMEOdt'
api_url = 'https://interface.bilibili.com/v2/playurl'

class BiliVideo(BiliBase):
    name = '哔哩哔哩 (Bilibili)'

    def get_page_info(self, info):
        page_index = match1(self.url, '\?p=(\d+)', 'index_(\d+)\.') or '1'
        html = get_content(self.url)
        data = match1(html, '__INITIAL_STATE__=({.+?});')
        self.logger.debug('data:\n%s', data)
        data = json.loads(data)['videoData']
        title = data['title']
        pages = data['pages']
        for page in pages:
            index = str(page['page'])
            subtitle = page['part']
            if index == page_index:
                self.mid = page['cid']
                if len(pages) > 1:
                    title = '{title} - {index} - {subtitle}'.format(**vars())
                elif subtitle and subtitle != title:
                    title = '{title} - {subtitle}'.format(**vars())
                info.duration = page['duration']
                break
        info.title = title
        info.artist = data['owner']['name']
        info.add_comment(data['tname'])

    def get_api_url(self, qn):
        params = {
            'appkey': APPKEY,
            'cid': self.mid,
            'platform': 'html5',
            'player': 0,
            'qn': qn
        }
        return sign_api_url(api_url, params, SECRETKEY)

    def prepare_list(self):
        vid = match1(self.url, '/(av\d+|(?:BV|bv)[0-9A-Za-z]{10})')
        if vid[:2] == 'av':
            vid = av2bv(vid)
        data = get_media_data(vid)

        if 'ugc_season' in data:
            bvids = [episode['bvid'] for episode in
                        sum((section['episodes'] for section in
                            data['ugc_season']['sections']), [])]
            self.set_index(vid, bvids)
            for bvid in bvids:
                yield 'https://www.bilibili.com/video/{bvid}/'.format(**vars())

        else:
            page = int(match1(self.url, '[^a-z]p(?:age)?=(\d+)',
                                        'index_(\d+)\.')
                       or '1')
            self.set_index(page, data['videos'])
            for p in range(data['videos']):
                p = p + 1
                yield 'https://www.bilibili.com/video/{vid}/?p={p}'.format(**vars())

site = BiliVideo()
