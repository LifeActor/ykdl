#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.html import get_content
from ..util.match import match1, matchall
from ..embedextractor import EmbedExtractor

import json

class Acfun(EmbedExtractor):

    name = u'ACfun 弹幕视频网'

    def prepare(self):
        html = get_content(self.url)
        pageInfo = json.loads(match1(html, u'<script>var pageInfo = (.+?)</script>'))
        title = pageInfo['title']

        sourceVid = match1(self.url, 'vid=([a-zA-Z0-9=]+)')
        if not sourceVid:
            sourceVid = match1(html, "data-vid=\"([a-zA-Z0-9=]+)\" data-")

        data = json.loads(get_content('http://www.acfun.cn/video/getVideo.aspx?id={}'.format(sourceVid)))
        sourceType = data['sourceType']
        sourceId = data['sourceId']
        sub_title = data['title']
        if sub_title != 'Part1' or len(pageInfo['videoList']) > 1:
            title = u'{} - {}'.format(title, sub_title)

        if sourceType == 'zhuzhan':
            sourceType = 'acorig'
            encode = data['encode']
            sourceId = (sourceId, encode)
        elif sourceType == 'letv':
            #workaround for letv, because it is letvcloud
            sourceType = 'le.letvcloud'
            sourceId = (sourceId, '2d8c027396')
        elif sourceType == 'qq':
            sourceType = 'qq.video'

        self.video_info['site'] = sourceType
        self.video_info['vid'] = sourceId
        self.video_info['title'] = title

    def prepare_playlist(self):

        html = get_content(self.url)

        videos = matchall(html, ['href="(/v/[a-zA-Z0-9_]+)" title="'])

        for v in videos:
            next_url = "http://www.acfun.cn{}".format(v)
            video_info = self.new_video_info()
            video_info['url'] = next_url
            self.video_info_list.append(video_info)

site = Acfun()
