# -*- coding: utf-8 -*-

from .._common import *


class DoubanMusic(Extractor):
    name = 'Douban Music (豆瓣音乐)'

    def prepare(self):
        info = MediaInfo(self.name)
        if not self.vid:
            self.vid = match1(self.url, 'sid=(\d+)')
        assert self.vid, 'No sid has been found!'

        data = get_response(
                'https://music.douban.com/j/artist/playlist',
                data={
                    'source' : '',
                    'sids' : self.vid,
                    'ck' : ''
                }).json()
        self.extract_song(info, data['songs'][0])
        return info

    def extract_song(self, info, song):
        artist = song['artist']
        info.title = song['title']
        info.artist = artist['name']
        info.duration = song['play_length']
        info.add_comment(song['label'])
        info.add_comment(artist['style'])
        info.refer = artist['url']
        info.streams['current'] = {
            'container': 'mp3',
            'video_profile': 'current',
            'src' : [song['url']],
            'size': 0
        }

    def parser_list(self, url):

        sids = match1(url, 'sid=([0-9,]+)')
        assert sids, 'No sid has been found!'

        data = get_response(
                'https://music.douban.com/j/artist/playlist',
                data={
                    'source' : '',
                    'sids' : sids,
                    'ck' : ''
                }).json()

        info_list = []
        for s in data['songs']:
            info = MediaInfo(self.name)
            self.extract_song(info, s)
            info_list.append(info)
        return info_list


site = DoubanMusic()
