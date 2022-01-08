# -*- coding: utf-8 -*-


def get_extractor(url):
    add_header('Referer', 'http://music.163.com/')

    if '/program' in url:
        from . import program as s
    elif '/dj' in url:
        from . import program as s
    elif '/mv' in url:
        from . import mv as s
    else:
        from . import music as s

    return s.site, url
