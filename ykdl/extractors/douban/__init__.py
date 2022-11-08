# -*- coding: utf-8 -*-


def get_extractor(url):
    if 'music.douban' in url and '/subject/' not in url or 'site.douban' in url:
        from . import music as s
        return s.site, url

    if 'movie.douban' in url and ('/trailer' in url or '/video' in url):
        from . import movie as s
        return s.site, url

    raise NotImplementedError(url)
