# -*- coding: utf-8 -*-

from ..._common import *
from .musicbase import NeteaseMusicBase


class NeteaseMusic(NeteaseMusicBase):
    name = 'Netease Music (网易云音乐)'
    api_url = 'http://music.163.com/api/song/detail/?id={}&ids=[{}]&csrf_token='

    def get_music(self, data):
        return data['songs'][0]

    def prepare_list(self):
        vid =  match1(self.url, '\?id=(.*)')
        params = {
            'id': vid,
            'csrf_token': ''
        }
        if 'album' in self.url:
            listdata =  get_response('http://music.163.com/api/album/' + vid,
                                     params=params).json()
            playlist = listdata['album']['songs']
        elif 'playlist' in self.url or 'toplist' in self.url:
            listdata =  get_response('http://music.163.com/api/playlist/detail',
                                     params=params).json()
            playlist = listdata['result']['tracks']
        elif 'artist' in self.url:
            listdata =  get_response('http://music.163.com/api/artist/' + vid,
                                     params=params).json()
            playlist = listdata['hotSongs']

        return [p['id'] for p in playlist]

site = NeteaseMusic()
