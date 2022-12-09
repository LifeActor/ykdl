# -*- coding: utf-8 -*-

from .._common import *


def get_info_list(sids):
    if not sids: return

    data = get_response('https://music.douban.com/j/artist/playlist',
                        data={
                            'source' : '',
                            'sids' : sids,
                            'ck' : ''
                        }).json()

    for song in data['songs']:
        info = MediaInfo(site.name)
        artist = song['artist']
        info.title = song['title']
        info.artist = artist['name']
        info.duration = song['play_length']
        info.add_comment(song['label'])
        info.add_comment(artist['style'])
        info.extra.referer = artist['url']
        info.streams['current'] = {
            'container': 'mp3',
            'profile': 'current',
            'src' : [song['url']],
        }
        yield info

class DoubanMusic(Extractor):
    name = 'Douban Music (豆瓣音乐)'

    def prepare_mid(self):
        return match1(self.url, 's(?:id)?=(\d+)')

    def prepare(self):
        return next(get_info_list(self.mid))

    def list_only(self):
        return 'site.douban' in self.url and not match(self.url, 's=\d+') or \
                match(self.url, 'sid=\d+,\d')

    def prepare_list(self):
        if 'site.douban' in self.url:
            sids = matchall(get_content(self.url), 'sid="(\d+)"')
        else:
            sids = matchall(match1(self.url, 'sid=([\d,]+)') or '', '(\d+)')

        sids, osids = [], sids
        for sid in osids:
            if sid not in sids:
                sids.append(sid)
        self.set_index(None, sids)
        return get_info_list(','.join(sids))

site = DoubanMusic()
