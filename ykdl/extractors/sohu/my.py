# -*- coding: utf-8 -*-

from .sohubase import SohuBase


class MySohu(SohuBase):
    name = '搜狐自媒体 (MySohu)'

    apiurl = 'http://my.tv.sohu.com/play/videonew.do'
    apiparams = {
        'vid': '',
        'referer': 'http://my.tv.sohu.com/'
    }

site = MySohu()
