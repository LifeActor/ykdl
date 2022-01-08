# -*- coding: utf-8 -*-

from ..._common import *
from .musicbase import NeteaseMusicBase


class NeteaseDj(NeteaseMusicBase):
    name = 'Netease Dj (网易电台)'
    api_url = 'http://music.163.com/api/dj/program/detail/?id={}&ids=[{}]&csrf_token='

    def get_music(self, data):
        return data['program']['mainSong']

    def prepare_list(self):
        vid =  match1(self.url, '\?id=([^&]+)')
        if 'djradio' in self.url:
            listdata =  get_response(
                            'http://music.163.com/api/dj/program/byradio/',
                            params={
                                'radioId': vid,
                                'ids': vid,
                                'csrf_token': '',
                            }).json()
            playlist = listdata['programs']
        return [p['id'] for p in playlist]

site = NeteaseDj()
