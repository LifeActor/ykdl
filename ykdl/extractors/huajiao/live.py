# -*- coding: utf-8 -*-

from .._common import *


class Huajiao(Extractor):
    name = 'huajiao (花椒直播)'

    def prepare_mid(self):
        html = get_content(self.url)
        return match1(html, '"sn":"([^"]+)')

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

        channel = match1(html, '"channel":"([^"]+)')
        encoded_json = get_response('http://g2.live.360.cn/liveplay',
                                    params={
                                        'stype': 'flv',
                                        'channel': channel,
                                        'bid': 'huajiao',
                                        'sn': self.mid,
                                        'sid': get_random_uuid_hex('SID'),
                                        '_rate': 'xd',
                                        'ts': time.time(),
                                        'r': random.random(),
                                        '_ostype': 'flash',
                                        '_delay': 0,
                                        '_sign': 'null',
                                        '_ver': 13
                                    }).content
        decoded_json = unb64(encoded_json[0:3] + encoded_json[6:])
        self.logger.debug('decoded_json:\n%s', decoded_json)
        data = json.loads(decoded_json)
        info.live = True
        info.streams['current'] = {
            'container': 'flv',
            'profile': 'current',
            'src' : [data['main']],
            'size': Infinity
        }
        return info

site = Huajiao()
