# -*- coding: utf-8 -*-

from .._common import *


def get_extractor(url):
    if '/v.' in url or 'iesdouyin.' in url:
        url = get_location(url)
    if '/live.' in url or 'amemv.com' in url:
        from . import live as s
    else:
        from . import video as s

    return s.site, url
