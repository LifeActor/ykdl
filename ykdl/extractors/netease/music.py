#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import hashlib
import base64

from ykdl.util.html import get_content, add_header
from ykdl.extractor import VideoExtractor
from ykdl.util.match import match1


def encrypted_id(dfsId):
    dfsId = str(dfsId)
    byte1 = bytearray('3go8&$8*3*3h0k(2)2', encoding='ascii')
    byte2 = bytearray(dfsId, encoding='ascii')
    byte1_len = len(byte1)
    for i in range(len(byte2)):
        byte2[i] = byte2[i] ^ byte1[i % byte1_len]
    m = hashlib.md5()
    m.update(byte2)
    result = base64.b64encode(m.digest()).decode('ascii')
    result = result.replace('/', '_')
    result = result.replace('+', '-')
    return result


def make_url(dfsId):
    encId = encrypted_id(dfsId)
    mp3_url = "http://m1.music.126.net/%s/%s.mp3" % (encId, dfsId)
    return mp3_url

class NeteaseMusic(VideoExtractor):
    name = u"Netease Music (网易云音乐)"

    supported_stream_types = ['hMusic', 'bMusic', 'mMusic', 'lMusic']
    song_date = {}
    def prepare(self):
        add_header("Referer", "http://music.163.com/")
        if not self.vid:
            self.vid =  match1(self.url, 'id=(.*)')

        api_url = "http://music.163.com/api/song/detail/?id={}&ids=[{}]&csrf_token=".format(self.vid, self.vid)
        music = json.loads(get_content(api_url))['songs'][0]

        self.title = music['name']
        self.artist = music['artists'][0]['name']

        for st in self.supported_stream_types:
            if st in music:
                self.stream_types.append(st)
                self.song_date[st] = music[st]
        
    def extract(self):
        stream_id = self.param.format or self.stream_types[0]
        song = self.song_date[stream_id]
        self.streams[stream_id] = {'container': song['extension'], 'video_profile': stream_id, 'src' : [make_url(song['dfsId'])], 'size': song['size']}

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
            self.title = music['name']
            self.artist = music['artists'][0]['name']
            for st in self.supported_stream_types:
                if st in music:
                    self.stream_types = []
                    self.stream_types.append(st)
                    self.song_date[st] = music[st]
            self.download_normal()

site = NeteaseMusic()
