# -*- coding: utf-8 -*-

from ..._common import *
from .musicbase import NeteaseMusicBase


class NeteaseDj(NeteaseMusicBase):
    name = 'Netease Dj (网易电台)'
    api_url = 'http://music.163.com/api/dj/program/detail/'

    def get_music(self, data):
        return data['program']['mainSong']

    def prepare_list(self):
        if 'djradio' in self.url:
            data =  get_response(
                        'http://music.163.com/api/dj/program/byradio/',
                        params={
                            'radioId': self.mid,
                            'ids': self.mid,
                            'csrf_token': '',
                        }).json()
            mids = [p['id'] for p in data['programs']]
            self.set_index(self.mid, mids)
            return mids

site = NeteaseDj()
