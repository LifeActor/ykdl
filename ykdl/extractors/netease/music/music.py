# -*- coding: utf-8 -*-

from ..._common import *
from .musicbase import NeteaseMusicBase


class NeteaseMusic(NeteaseMusicBase):
    name = 'Netease Music (网易云音乐)'
    api_url = 'http://music.163.com/api/song/detail/'

    def get_music(self, data):
        return data['songs'][0]

    def prepare_list(self):
        params = {
            'id': self.mid,
            'csrf_token': ''
        }
        if 'album' in self.url:
            data =  get_response('http://music.163.com/api/album/' + self.mid,
                                 params=params).json()
            playlist = data['album']['songs']
        elif 'playlist' in self.url or 'toplist' in self.url:
            data =  get_response('http://music.163.com/api/playlist/detail',
                                 params=params).json()
            playlist = data['result']['tracks']
        elif 'artist' in self.url:
            data =  get_response('http://music.163.com/api/artist/' + self.mid,
                                 params=params).json()
            playlist = data['hotSongs']

        mids = [p['id'] for p in playlist]
        self.set_index(self.mid, mids)
        return mids

site = NeteaseMusic()
