#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import (get_content, get_location, add_header,
                            add_default_handler, install_default_handlers)
from ykdl.util.match import match1, matchall
from ykdl.compact import HTTPCookieProcessor

from .idconvertor import av2bv

import json


API_view = 'https://api.bilibili.com/x/web-interface/view?bvid='


add_default_handler(HTTPCookieProcessor)
install_default_handlers()
add_header('Referer', 'https://www.bilibili.com/')

def get_extractor(url):
    if 'live.bilibili' in url:
        from . import live as s
        return s.site, url
    elif 'vc.bilibili' in url:
        from . import vc as s
        return s.site, url
    elif '/bangumi/' in url:
        from . import bangumi as s
        return s.site, url

    page_index = match1(url, '(?:page|\?p)=(\d+)', 'index_(\d+)\.') or '1'

    av_id = match1(url, '(?:/av|aid=)(\d+)')
    if av_id:
        bv_id = av2bv(av_id)
    else:
        bv_id = match1(url, '((?:BV|bv)[0-9A-Za-z]{10})')

    if bv_id:
        try:
            data = json.loads(get_content(API_view + bv_id))
            assert data['code'] == 0, "can't play this video!!"
            url = data['data']['redirect_url']
        except AssertionError:
            raise
        except:
            url = 'https://www.bilibili.com/video/' + bv_id
    else:
        url = get_location(url)

    if '/bangumi/' in url:
        from . import bangumi as s
    else:
        if page_index > '1':
            url = '{}?p={}'.format(url, page_index)
        from . import video as s

    return s.site, url
