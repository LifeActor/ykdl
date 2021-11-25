# -*- coding: utf-8 -*-

from .sohubase import SohuBase


class TvSohu(SohuBase):
    name = '搜狐视频 (TvSohu)'

    apiurl = 'http://hot.vrs.sohu.com/vrs_flash.action'
    apiparams = {'vid': ''}

site = TvSohu()
