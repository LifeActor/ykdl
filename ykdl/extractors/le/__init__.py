# -*- coding: utf-8 -*-

from .._common import *


def get_extractor(url):
    add_header('User-Agent',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) '
               'AppleWebKit/603.1.30 (KHTML, like Gecko) '
               'Version/10.1 Safari/603.1.30')

    if 'lunbo' in url:
        from . import lunbo as s
    elif match(url, 'live[\./]|/izt/'):
        from . import live as s
    elif 'bcloud' in url:
        from . import letvcloud as s
    else:
        from . import le as s

    return s.site, url
