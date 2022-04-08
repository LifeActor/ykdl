# -*- coding: utf-8 -*-

from .._common import *


def get_extractor(url):
    if '/live.' in url:
        from . import live as s
    else:
        from . import video as s

    return s.site, url
