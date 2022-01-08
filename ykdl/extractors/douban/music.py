# -*- coding: utf-8 -*-

from .._common import *


def get_info_list(sids):
    data = get_response('https://music.douban.com/j/artist/playlist',
                        data={
                            'source' : '',
                            'sids' : sids,
                            'ck' : ''
                        }).json()

    info_list = []
    for song in data['songs']:
        info = MediaInfo(site.name)
        info_list.append(info)
        artist = song['artist']
        info.title = song['title']
        info.artist = artist['name']
        info.duration = song['play_length']
        info.add_comment(song['label'])
        info.add_comment(artist['style'])
        info.extra['referer'] = artist['url']
        info.streams['current'] = {
            'container': 'mp3',
            'video_profile': 'current',
            'src' : [(artist['picture'], song['url'])],
            'size': 0
        }
    assert info_list, "can't find songs of %r, may has been removed!" % sids
    return info_list

class DoubanMusic(Extractor):
    name = 'Douban Music (豆瓣音乐)'

    def prepare(self):
        info = MediaInfo(self.name)
        if not self.vid:
            self.vid = match1(self.url, 's(?:id)?=(\d+)')
        assert self.vid, 'No sid has been found!'

        return get_info_list(self.vid)[0]

    def list_only(self):
        return 'site.douban' in self.url and not match(self.url, 's=(\d+)') or \
                match(self.url, 'sid=\d+,(\d)')

    def prepare_list(self):

        if 'site.douban' in self.url:
            sids = matchall(get_content(self.url), 'sid="(\d+)"')
        else:
            sids = matchall(match1(self.url, 'sid=([\d,]+)') or '', '(\d+)')
        assert sids, 'No sid has been found!'

        sids, osids = [], sids
        for sid in osids:
            if sid not in sids:
                sids.append(sid)
        sids = ','.join(sids)
        return get_info_list(sids)


site = DoubanMusic()
