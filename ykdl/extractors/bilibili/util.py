# -*- coding: utf-8 -*-

from .._common import *
from .idconvertor import *


__all__ = ['av2bv', 'sign_api_url', 'get_media_data']

def sign_api_url(api_url, params, skey):
    params = sorted(params.items())
    params.append(('sign', hash.md5(urlencode(params) + skey)))
    params_str = urlencode(params)
    return '{api_url}?{params_str}'.format(**vars())

def get_media_data(bvid):
    data = get_response('https://api.bilibili.com/x/web-interface/view',
                        params={'bvid': bvid}).json()
    assert data['code'] == 0, "can't play this video!!"
    return data['data']
