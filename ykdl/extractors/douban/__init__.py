# -*- coding: utf-8 -*-


def get_extractor(url):
    if 'music.douban' in url:
        from . import music as s
        return s.site, url

    raise NotImplementedError(url)
