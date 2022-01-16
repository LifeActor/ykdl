# -*- coding: utf-8 -*-

from .._common import *


class BaiduMusic(Extractor):
    name = 'BaiduMusic (百度音乐)'


    def prepare(self):
        info = MediaInfo(self.name)
        if not self.vid:
            self.vid = match1(self.url, 'http://music.baidu.com/song/([\d]+)')

        api = 'http://play.baidu.com/data/music/songlink'
        data = {'songIds': self.vid}
        song_data = get_response(api, data=data).json()['data']['songList'][0]

        info.title = song_data['songName']
        info.artist = song_data['artistName']

        info.streams['current'] = {
            'container': song_data['format'],
            'video_profile': 'current',
            'src' : [song_data['songLink']],
            'size': song_data['size']
        }
        return info

    def prepare_list(self):

        album_id = match1(self.url, 'http://music.baidu.com/album/([\d]+)')
        api = 'http://play.baidu.com/data/music/box/album'
        params = {
            'albumId': album_id,
            'type': 'album',
            '_': time.time()
        }
        data = get_response(api, params=params).json()

        self.logger.info('album:\n\t%s', data['data']['albumName'])

        return data['data']['songIdList']

site = BaiduMusic()
