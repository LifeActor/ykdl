# -*- coding: utf-8 -*-

from .._common import *
from .idconvertor import av2bv


def get_extractor(url):
    install_cookie()
    add_header('Referer', 'https://www.bilibili.com/')

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
            data = get_response('https://api.bilibili.com/x/web-interface/view',
                                params={'bvid': bv_id}).json()
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
            url = '{url}?p={page_index}'.format(**vars())
        from . import video as s

    return s.site, url
