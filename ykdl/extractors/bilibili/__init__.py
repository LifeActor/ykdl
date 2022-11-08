# -*- coding: utf-8 -*-

from .._common import *
from .util import *

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

    bv_id = match1(url, r'\b((?:BV|bv)[0-9A-Za-z]{10})')
    if not bv_id:
        av_id = match1(url, r'\b(?:av|aid=)(\d+)')
        if av_id:
            bv_id = av2bv(av_id)

    if bv_id:
        data = get_media_data(bv_id)
        forward = data.get('forward')
        if forward:
            from .video import site
            forward = av2bv(forward)
            site.logger.warning('视频撞车了! 从 %s 跳转至首发 %s', bv_id, forward)
            bv_id = forward
            data = get_media_data(bv_id)
        url = data.get('redirect_url') or \
              'https://www.bilibili.com/video/{bv_id}/'.format(**vars())
    else:
        url = get_location(url)

    if '/bangumi/' in url:
        from . import bangumi as s
    else:
        if page_index > '1':
            url = '{url}?p={page_index}'.format(**vars())
        from . import video as s

    return s.site, url
