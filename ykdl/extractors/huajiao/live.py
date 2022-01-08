# -*- coding: utf-8 -*-

from .._common import *


class Huajiao(Extractor):
    name = 'huajiao (花椒直播)'

    def prepare(self):
        info = MediaInfo(self.name, True)
        html = get_content(self.url)
        t_a = match1(html, '"keywords" content="([^"]+)')
        info.title = t_a.split(',')[0]
        info.artist = t_a.split(',')[1]

        replay_url = match1(html, '"m3u8":\s?("[^"]+)"')
        if replay_url and len(replay_url) > 2:
            replay_url = json.loads(replay_url)
            info.live = False
            info.streams = load_m3u8_playlist(replay_url)
            return info

        self.vid = match1(html, '"sn":"([^"]+)')
        channel = match1(html, '"channel":"([^"]+)')
        encoded_json = get_response('http://g2.live.360.cn/liveplay',
                                    params={
                                        'stype': 'flv',
                                        'channel': channel,
                                        'bid': 'huajiao',
                                        'sn': self.vid,
                                        'sid': get_random_uuid_hex('SID'),
                                        '_rate': 'xd',
                                        'ts': time.time(),
                                        'r': random.random(),
                                        '_ostype': 'flash',
                                        '_delay': 0,
                                        '_sign': 'null',
                                        '_ver': 13
                                    }).content
        decoded_json = base64.b64decode(encoded_json[0:3] + encoded_json[6:])
        video_data = json.loads(decoded_json.decode())
        live_url = video_data['main']
        info.live = True
        info.streams['current'] = {
            'container': 'flv',
            'video_profile': 'current',
            'src' : [live_url],
            'size': float('inf')
        }
        return info

site = Huajiao()
