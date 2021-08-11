#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_location


def get_extractor(url):
    if '/v.' in url:
        url = get_location(url)
    if '/live.' in url or 'amemv.com' in url:
        from . import live as s
    else:
        from . import video as s

    return s.site, url
