#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import hashlib
import base64

from ykdl.util.html import get_content, add_header
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
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


def make_url(host, dfsId):
    encId = encrypted_id(dfsId)
    mp3_url = "http://m{}.music.126.net/{}/{}.mp3".format(host, encId, dfsId)
    return mp3_url

class NeteaseMusicBase(VideoExtractor):

    supported_stream_types = ['hMusic', 'bMusic', 'mMusic', 'lMusic']
    song_date = {}
    def prepare(self):
        info = VideoInfo(self.name)
        add_header("Referer", "http://music.163.com/")
        if not self.vid:
            self.vid =  match1(self.url, 'id=(.*)')

        api_url = self.api_url.format(self.vid, self.vid)
        music = self.get_music(json.loads(get_content(api_url)))

        info.title = music['name']
        info.artist = music['artists'][0]['name']

        self.mp3_host = music['mp3Url'][8]

        for st in self.supported_stream_types:
            if st in music and music[st]:
                info.stream_types.append(st)
                self.song_date[st] = music[st]
                self.extract_song(info)
        return info

    def extract_song(self, info):
        for stream_id in info.stream_types:
            song = self.song_date[stream_id]
            info.streams[stream_id] = {'container': 'mp3', 'video_profile': stream_id, 'src' : [make_url(self.mp3_host, song['dfsId'])], 'size': song['size']}
