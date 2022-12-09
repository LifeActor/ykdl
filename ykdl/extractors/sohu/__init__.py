# -*- coding: utf-8 -*-

from .._common import *


def get_extractor(url):
    path_b64 = match1(url, 'tv.sohu.com/v/(\w+=*)')
    if path_b64:
        path = unb64(path_b64, urlsafe=True)
        if fullmatch(path, '[a-z]{2}/\d+/\d+\.shtml'):
            url = 'https://my.tv.sohu.com/' + path

    if 'my.tv.sohu.com' in url:
        from . import my as s
        return s.site, url
    else:
        from . import tv as s
        return s.site, url

    raise NotImplementedError(url)
