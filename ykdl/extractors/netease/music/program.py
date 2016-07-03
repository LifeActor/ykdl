#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from .musicbase import NeteaseMusicBase
from ykdl.videoinfo import VideoInfo
from ykdl.util.html import get_content, add_header
from ykdl.util.match import match1

class NeteaseDj(NeteaseMusicBase):
    name = u'Netease Dj (网易电台)'
    api_url = "http://music.163.com/api/dj/program/detail/?id={}&ids=[{}]&csrf_token="

    def get_music(self, data):
       return data["program"]["mainSong"]

    def parser_list(self, url):

        add_header("Referer", "http://music.163.com/")
        vid =  match1(url, 'id=([^&]+)')
        if "djradio" in url:
           api_url = "http://music.163.com/api/dj/program/byradio/?radioId={}&ids=[{}]&csrf_token=".format(vid, vid)
           listdata = json.loads(get_content(api_url))
           playlist = listdata['programs']

        info_list = []
        for music in playlist:
            info = VideoInfo(self.name)
            info.title = music['name']
            data = music['mainSong']
            self.mp3_host = data['mp3Url'][8]
            for st in self.supported_stream_types:
                if st in data and data[st]:
                    info.stream_types.append(st)
                    self.song_date[st] = data[st]
            self.extract_song(info)
            info_list.append(info)
        return info_list

site = NeteaseDj()
