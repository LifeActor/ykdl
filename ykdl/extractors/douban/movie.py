# -*- coding: utf-8 -*-

from .._common import *


class DoubanMovie(Extractor):
    name = 'Douban movie (豆瓣电影)'

    def prepare(self):
        info = MediaInfo(self.name)
        html = get_content(self.url)
        info.title = match1(html, '<meta name="description" content='
                                  '"(.+?) 在线观看"/>')
        url = match1(html,'"embedUrl": "(.+?)"')

        info.streams['current'] = {
            'container': 'mp4',
            'profile': 'current',
            'src': [url]
        }
        return info

    def list_only(self):
        return '/subject/' in self.url

    def prepare_list(self):
        html = get_content(self.url)
        return matchall(html, '<a class="pr-video" href="'
                              '(https://movie.douban.com/trailer/\d+/)#')

site = DoubanMovie()
