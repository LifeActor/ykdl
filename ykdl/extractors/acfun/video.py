# -*- coding: utf-8 -*-

from .._common import *
from .acbase import AcBase


class AcVideo(AcBase):

    name = 'AcFun 弹幕视频网'

    def get_page_info(self, html):
        pageInfo = json.loads(match1(html, '(?:pageInfo|videoInfo) = ({.+?});'))
        videoList = pageInfo['videoList']
        videoInfo = pageInfo.get('currentVideoInfo')
        assert videoInfo, bgmInfo.get('playErrorMessage') or "can't play this video!!"

        title = pageInfo['title']
        sub_title = videoInfo['title']
        artist = pageInfo['user']['name']
        if sub_title not in ('noTitle', 'Part1', title) or len(videoList) > 1:
            title = '{title} - {sub_title}'.format(**vars())
        sourceVid = videoInfo['id']

        m3u8Info = videoInfo.get('playInfos')
        if m3u8Info:
            m3u8Info = m3u8Info[0]
        else:
            m3u8Info = videoInfo.get('ksPlayJson')

        return title, artist, sourceVid, m3u8Info

    def format_mid(self, mid):
        assert fullmatch(mid, '(ac)?\d+')
        mid = match1(mid, '(\d+)')
        # force rebuild url for list index
        self.url = 'https://www.acfun.cn/v/ac{mid}'.format(**vars())
        return mid

    def prepare_mid(self):
        return match1(self.url, 'v/ac(\d+)', r'\bac=(\d+)')

    def prepare_list(self):
        html = get_content(self.url)
        videos = ['https://www.acfun.cn' + path for path in
                  matchall(html, 'href=[\'"](/v/ac[0-9_]+)[\'"] title=[\'"]')]
        self.set_index(self.url, videos)
        return videos

site = AcVideo()
