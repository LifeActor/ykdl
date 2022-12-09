# -*- coding: utf-8 -*-

from ._common import *


class Ku6(SimpleExtractor):
    name = '酷6 (Ku6)'

    def init(self):
        self.url_pattern = 'flvURL: "([^"]+)'
        self.title_pattern = 'title = "([^"]+)'
        pass

    def list_only(self):
        return match(self.url, 'https://www.ku6.com/detail/\d+')

    def prepare_list(self):
        html = get_content(self.url)
        videos = matchall(html, "'title': '(.+?)',[\s\S]+?'playUrl': '(.+?)',")
        videos.reverse()
        self.set_index(None, videos)
        for title, url in videos:
            info = MediaInfo(self.name)
            info.title = title
            info.streams['current'] = {
                'container': 'mp4',
                'src': [url]
            }
            yield info

site = Ku6()
