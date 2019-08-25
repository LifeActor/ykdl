#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1, matchall
from ykdl.compact import urlencode

import json
import time

from .acbase import AcBase


class AcBan(AcBase):

    name = u'AcFun 弹幕视频网 (番剧)'

    def list_only(self):
        return '/bangumi/aa' in self.url

    def get_page_info(self, html):
        artist = None
        bgmInfo = json.loads(match1(html, u'window.bangumiData = ({.+?});'))
        videoInfo = bgmInfo['currentVideoInfo']
        title = u'{} - {}'.format(
                bgmInfo['bangumiTitle'],
                bgmInfo['episodeName'],
        )
        sourceVid = videoInfo['id']
        m3u8Info = videoInfo.get('playInfos')
        if m3u8Info:
            m3u8Info = m3u8Info[0]

        return title, artist, sourceVid, m3u8Info

    def get_path_list(self):
        albumId = match1(self.url, '/a[ab](\d+)')
        if self.list_only():
            html = get_content(self.url)
        else:
            html = get_content('https://www.acfun.cn/bangumi/aa' + albumId)
        groupId = match1(html, '"groups":[{[^}]*?"id":(\d+)')
        contentsCount = int(match1(html, '"contentsCount":(\d+)'))

        params = {
            'albumId': albumId,
            'groupId': groupId,
            'num': 1,
            'size': max(contentsCount, 20),
            '_': int(time.time() * 1000),
        }
        data = json.loads(get_content('https://www.acfun.cn/album/abm/bangumis/video?' + urlencode(params)))
        videos = []
        for c in data['data']['content']:
            vid = c['videos'][0]['id']
            v = '/bangumi/ab{}_{}_{}'.format(albumId, groupId, vid)
            videos.append(v)

        return videos

site = AcBan()
