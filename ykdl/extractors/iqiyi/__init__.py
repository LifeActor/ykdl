# -*- coding: utf-8 -*-

from .._common import get_location

import re

def get_extractor(url):
    if 'gamelive' in url:
        url = get_location(url)
    if 'pps.' in url:
        from .. import pps as s
    elif 'live.iqiyi' in url:
        from . import live as s
    else:
        from . import video as s

    return s.site, url
