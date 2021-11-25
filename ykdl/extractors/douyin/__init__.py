# -*- coding: utf-8 -*-

from .._common import *


def get_extractor(url):
    if '/v.' in url:
        add_header('User-Agent',
                   'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) '
                   'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 '
                   'Mobile/15E148 Safari/604.1')
        url = get_location(url)
    if '/live.' in url or 'amemv.com' in url:
        from . import live as s
    else:
        from . import video as s

    return s.site, url
