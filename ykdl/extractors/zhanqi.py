# -*- coding: utf-8 -*-

from ._common import *


class Zhanqi(Extractor):
    # live is down, all are playback
    name = '战旗 (zhanqi)'

    def prepare(self):
        info = MediaInfo(self.name)
        install_cookie()

        html = get_content(self.url)
        data = json.loads(match1(html, 'oPageConfig.oVideo = ({.+?});',
                                       'oPageConfig.oRoom = ({.+?});'))
        info.title = data['title']
        info.artist = data['nickname']
        if data.get('protocol') == 'hls':
            info.streams = load_m3u8_playlist(data['playUrl'])
            return info

        vid = data['videoId']
        gid = get_response('https://www.zhanqi.tv/api/public/room.viewer',
                           params={'uid': data['uid']}
                           ).json()['data']['gid']
        chain_key = get_response(
                        'https://www.zhanqi.tv/api/public/burglar/chain',
                        data={
                            'stream': vid + '.flv',
                            'cdnKey': 202,
                            'platform': 128
                        }).json()['data']['key']
        pn = str(int(time.time() * 1e6))[-11:]
        cdn_host = random.choice(get_response(
                        'https://umc.danuoyi.alicdn.com/dns_resolve_https',
                        params={
                            'app': 'zqlive',
                            'host_key': 'alhdl-cdn.zhanqi.tv',
                            'stream': vid,
                            'playNum': pn,
                            'protocol': 'hdl',
                            #'client_ip': '',
                            'gId': gid,
                            'platform': 128
                        }).json()['redirect_domain'])

        # valid stream suffix: 1080p 720p 408p 360p
        url = ('https://{cdn_host}/alhdl-cdn.zhanqi.tv/zqlive/'
               '{vid}.flv?{chain_key}&'.format(**vars())
              + urlencode({
                    'playNum': '{pn}',
                    'gId': gid,
                    'ipFrom': 1,
                    'clientIp': '',
                    'fhost': 'h5',
                    'platform': 128
                }))
        info.streams['current'] = {
            'container': 'flv',
            'profile': 'current',
            'src': [url]
        }
        return info

site = Zhanqi()
