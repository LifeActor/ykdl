# -*- coding: utf-8 -*-

from .._common import *
from .idconvertor import *


__all__ = ['av2bv', 'sign_api_url', 'get_media_data']

def sign_api_url(api_url, params_str, skey):
    sign = hash.md5(params_str + skey)
    return '{api_url}?{params_str}&sign={sign}'.format(**vars())

def get_media_data(bvid):
    data = get_response('https://api.bilibili.com/x/web-interface/view',
                        params={'bvid': bvid}).json()
    assert data['code'] == 0, "can't play this video!!"
    return data['data']
