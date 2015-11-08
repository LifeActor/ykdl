#!/usr/bin/env python

from ..util.html import get_content
from ..common import playlist_not_supported
from ..util.match import match1, matchall
from ..embedextractor import EmbedExtractor

import re
import json

class Acfun(EmbedExtractor):

    def prepare(self, **kwargs):
        assert self.url
        assert re.match(r'http://[^\.]+.acfun.[^\.]+/\D/\D\D(\d+)', self.url)

        html = get_content(self.url)

        self.title = match1(html, '<h1 id="txt-title-view">([^<>]+)<')
        videos = matchall(html,["data-vid=\"(\d+)\""])

        for video in videos:
            info = json.loads(get_content('http://www.acfun.tv/video/getVideo.aspx?id=' + video))
            sourceType = info['sourceType']

            if sourceType == 'letv':
                #workaround for letv, because it is letvcloud
                sourceType = 'letvcloud'
                sourceId = (info['sourceId'], '2d8c027396')
            if sourceType == 'zhuzhan':
                sourceType = 'acorig'
                sourceId = video
            else:
                sourceId = info['sourceId']

            self.video_info.append((sourceType, sourceId))

site = Acfun()
download = site.download
download_playlist = playlist_not_supported('acfun')
