# -*- coding: utf-8 -*-

from .._common import *


class NeteaseLive(Extractor):
    name = '网易CC直播 (163)'

    def prepare(self):
        info = MediaInfo(self.name, True)
        if not self.vid:
            html = get_content(self.url)
            raw_data = match1(html, '<script id="__NEXT_DATA__".*?>(.*?)</script>')
            data = json.loads(raw_data)
            self.logger.debug('video_data:\n%s', data)
            try:
                data = data['props']['pageProps']['roomInfoInitData']
                self.vid = data['live']['ccid']
                info.title = data['live']['title']
                info.artist = data['micfirst']['nickname']
            except KeyError:
                # project, select first living room
                data = data['props']['pageProps']['data']
                rooms = data['module_infos'][0]['content']
                for room in rooms:
                    self.vid = room['ccid']
                    info.artist = room['name']
                    if room['is_living']:
                        break
                info.title = data['share_title']
            assert self.vid, 'live video is offline'

        data = get_response('http://cgi.v.cc.163.com/video_play_url/{self.vid}'
                            .format(**vars())).json()

        info.streams['current'] = {
            'container': 'flv',
            'video_profile': 'current',
            'src': [data['videourl']],
            'size': 0
        }
        return info

site = NeteaseLive()
