# -*- coding: utf-8 -*-

from .._common import *


def get_playback(vid):
    from .le import Letv
    site = Letv()
    site.name = 'Le Live(乐视直播回看)'
    site.vid = vid
    return site.prepare()

class LeLive(Extractor):
    name = 'Le Live(乐视直播)'

    stream_2_id_profile = {
        'flv_1080p3m': ['BD', '1080p'],
        'flv_1080p'  : ['BD', '1080p'],
        'flv_1300'   : ['TD',  '超清'],
        'flv_1000'   : ['HD',  '高清'],
        'flv_720p'   : ['SD',  '标清'],
        'flv_350'    : ['LD',  '流畅']
    }

    def prepare(self):
        self.vid = match1(self.url, 'd=(\d+)', 'live/(\d+)')
        if '/izt/' in self.url:
            vid = self.vid
            if not vid:
                html = get_content(self.url)
                vid = match1(html, 'vid\s*:\s*"(\d+)",', 'vid="(\d+)"')
            return get_playback(vid)
        else:
            if not self.vid:
                html = get_content(self.url)
                self.vid = match1(html, 'liveId\s*:\s*"(\d+)"')

        live_data = get_response(
                'http://api.live.letv.com/v1/liveRoom/single/1001', 
                params={'id': self.vid}).json()
        if live_data.get('status') != 2:
            return get_playback(live_data['recordingId'])

        # live video is dead, the followed code will not be used
        live_data = get_response(
                'http://player.pc.le.com/player/startup_by_pid/1001/'
                + self.vid,
                params={'host': 'live.le.com'}).json()

        info = MediaInfo(self.name, True)
        info.title = live_data['title']

        for st in live_data['rows']:
            stream, profile = self.stream_2_id_profile[st['rateType']]
            data = get_response(st['streamUrl'],
                                params={
                                    'format': 1,
                                    'expect': 2,
                                    'termid': 1,
                                    'platid': 10,
                                    'playid': 1,
                                    'sign': 'live_web',
                                    'splatid': 1001,
                                    'vkit': 20161017,
                                    'station': self.vid
                                }).json()
            src = data['location']
            info.streams[stream] = {
                'container': 'm3u8',
                'video_profile': profile,
                'size' : float('inf'),
                'src' : [src]
            }

        return info

    def prepare_list(self):
        html = get_content(self.url)
        vids = matchall(html, 'vid="(\d+)"')
        # fake urls
        return ['http://live.le.com/izt/vid={}'.format(vid) for vid in vids]

site = LeLive()
