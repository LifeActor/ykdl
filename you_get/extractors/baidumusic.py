#!/usr/bin/env python3

from ..util.match import match1
from ..util.html import get_content
from ..extractor import VideoExtractor
import time
from  urllib import parse
import json

class BaiduMusic(VideoExtractor):
    name = 'BaiduMusic (百度音乐)'


    def prepare(self):
        assert self.url or self.vid

        if not self.vid:
            self.vid = match1(self.url, 'http://music.baidu.com/song/([\d]+)')

        param = parse.urlencode({'songIds': self.vid})

        song_data = json.loads(get_content('http://play.baidu.com/data/music/songlink', data=bytes(param, 'utf-8')))['data']['songList'][0]

        self.title = song_data['songName']
        self.artist = song_data['artistName']

        self.stream_types.append('current')
        self.streams['current'] = {'container': song_data['format'], 'video_profile': 'current', 'src' : [song_data['songLink']], 'size': song_data['size']}

    def download_playlist(self, url, param):

        album_id = match1(url, 'http://music.baidu.com/album/([\d]+)')
        data = json.loads(get_content('http://play.baidu.com/data/music/box/album?albumId={}&type=album&_={}'.format(album_id, time.time())))

        print('album:		%s' % data['data']['albumName'])

        for s in data['data']['songIdList']:
            self.download(s, param)

site = BaiduMusic()
