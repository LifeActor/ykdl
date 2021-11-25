# -*- coding: utf-8 -*-

from .sohubase import SohuBase


class EduSohu(SohuBase):
    name = '搜狐课堂 (Sohu Edu)'

    apiurl = 'http://my.tv.sohu.com/play/videonew.do'
    apiparams = {
        'vid': '',
        'referer': 'http://edu.tv.sohu.com/'
    }

site = EduSohu()
