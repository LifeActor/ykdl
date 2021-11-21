# -*- coding: utf-8 -*-

from ._common import *


class BoBo(VideoExtractor):
    name = 'bobo娱乐 美女直播'

    def prepare(self):
        add_default_handler(HTTPCookieProcessor)
        install_default_handlers()

        info = VideoInfo(self.name, True)
        html = get_content(self.url)
        self.vid = match1(html, '"userNum":(\d+)')
        live_id = match1(html, '"liveId":\s*(\d+)')
        assert live_id, '主播正在休息'

        url = 'http://extapi.live.netease.com/redirect/video/' + self.vid
        info.stream_types.append('current')
        info.streams['current'] = {
            'container': 'mp4',
            'src': [url],
            'size' : float('inf')
        }
        info.artist = match1(html, '"nick":"([^"]+)')
        info.title = match1(html, '<title>([^<]+)').split('-')[0]
        return info

site = BoBo()
