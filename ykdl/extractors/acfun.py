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

        sourceVid = match1(html, "data-vid=\"([a-zA-Z0-9=]+)\" data-")

        data = json.loads(get_content('http://www.acfun.tv/video/getVideo.aspx?id={}'.format(sourceVid)))
        sourceType = data['sourceType']
        sourceId = data['sourceId']

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

        self.video_info=(sourceType, sourceId)

    def prepare_playlist(self):

        html = get_content(self.url)

        videos = matchall(html, ['href="(\/v\/[a-zA-Z0-9_]+)" title="'])

        for v in videos:
            next_url = "http://www.acfun.tv/{}".format(v)
            self.video_info_list.append(('acfun', next_url))

site = Acfun()
