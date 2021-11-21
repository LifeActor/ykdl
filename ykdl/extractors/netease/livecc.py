# -*- coding: utf-8 -*-

from .._common import *


class NeteaseLive(VideoExtractor):
    name = '网易CC直播 (163)'

    def prepare(self):
        info = VideoInfo(self.name, True)
        if not self.vid:
            html = get_content(self.url)
            raw_data = match1(html, '<script id="__NEXT_DATA__".*?>(.*?)</script>')
            data = json.loads(raw_data)
            self.logger.debug('video_data:\n%s', data)
            data = data['props']['pageProps']['roomInfoInitData']
            self.vid = data['live']['ccid']
            assert self.vid != 0, 'live video is offline'
            info.title = data['live']['title']
            info.artist = data['micfirst']['nickname']

        data = get_content(
                'http://cgi.v.cc.163.com/video_play_url/' + self.vid).json()

        info.stream_types.append('current')
        info.streams['current'] = {
            'container': 'flv',
            'video_profile': 'current',
            'src': [data['videourl']],
            'size': 0
        }
        return info

site = NeteaseLive()
