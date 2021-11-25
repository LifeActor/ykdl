# -*- coding: utf-8 -*-


def get_extractor(url):
    if 'v.douyu' in url or 'vmobile.douyu' in url:
        from . import video as s
    else:
        from . import live as s

    return s.site, url
