#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from .musicbase import NeteaseMusicBase
from ykdl.util.html import get_content, add_header
from ykdl.util.match import match1


class NeteaseMusic(NeteaseMusicBase):
    name = u"Netease Music (网易云音乐)"
    api_url = "http://music.163.com/api/song/detail/?id={}&ids=[{}]&csrf_token="

    def get_music(self, data):
       return data['songs'][0]

    def download_playlist(self, url, param):
        self.param = param
        add_header("Referer", "http://music.163.com/")
        vid =  match1(url, 'id=(.*)')
        if "album" in url:
           api_url = "http://music.163.com/api/album/{}?id={}&csrf_token=".format(vid, vid)
           listdata = json.loads(get_content(api_url))
           playlist = listdata['album']['songs']
        elif "playlist" in url:
           api_url = "http://music.163.com/api/playlist/detail?id={}&csrf_token=".format(vid)
           listdata = json.loads(get_content(api_url))
           playlist = listdata['result']['tracks']
        elif "toplist" in url:
           api_url = "http://music.163.com/api/playlist/detail?id={}&csrf_token=".format(vid)
           listdata = json.loads(get_content(api_url))
           playlist = listdata['result']['tracks']
        elif "artist" in url:
           api_url = "http://music.163.com/api/artist/{}?id={}&csrf_token=".format(vid, vid)
           listdata = json.loads(get_content(api_url))
           playlist = listdata['hotSongs']

        for music in playlist:
            self.stream_types = []
            self.title = music['name']
            self.artist = music['artists'][0]['name']
            self.mp3_host = music['mp3Url'][8]
            for st in self.supported_stream_types:
                if st in music and music[st]:
                    self.stream_types.append(st)
                    self.song_date[st] = music[st]
            self.download_normal()

site = NeteaseMusic()
