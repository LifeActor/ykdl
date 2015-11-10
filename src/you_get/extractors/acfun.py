#!/usr/bin/env python

from ..util.html import get_content
from ..util.match import match1, matchall
from ..embedextractor import EmbedExtractor

class Acfun(EmbedExtractor):

    def prepare(self, **kwargs):
        assert self.url

        html = get_content(self.url)

        self.title = match1(html, '<h1 id="txt-title-view">([^<>]+)<')

        sourceType = match1(html, "data-from=\"([a-zA-Z0-9]+)\" data-did=")
        sourceId = match1(html, "data-did=\"\" data-sid=\"([a-zA-Z0-9=]+)\"")
        sourceVid = match1(html, "data-vid=\"([a-zA-Z0-9=]+)\" data-scode=")

        if sourceType == 'zhuzhan':
            sourceType = 'acorig'
            sourceId = sourceVid
        elif sourceType == 'letv':
            #workaround for letv, because it is letvcloud
            sourceType = 'letvcloud'
            sourceId = (sourceId, '2d8c027396')

        self.video_info.append((sourceType, sourceId))

    def download_playlist_by_url(self, url, param, **kwargs):
        self.url = url

        html = get_content(self.url)

        videos = matchall(html, ['href="([\/a-zA-Z0-9_]+)" title="Part'])
        print(videos)
        for v in videos:
            next_url = "http://www.acfun.tv/{}".format(v)
            self.download(next_url, param, **kwargs)

site = Acfun()
download = site.download
download_playlist = site.download_playlist_by_url
