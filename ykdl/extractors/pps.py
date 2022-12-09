# -*- coding: utf-8 -*-

from ._common import *


def gsign(params):
    s = []
    for key in sorted(params.keys()):
        s.append('{}:{}'.format(key, params[key]))
    s.append('w!ytDgy#lEXWoJmN4HPf')
    return hash.sha1(''.join(s))

def getlive(mid, rate='source'):
    params = {
        'type_id': 1,
        'vid': 1,
        'anchor_id': mid,
        'app_key': 'show_web_h5',
        'version': '1.0.0',
        'platform': '1_10_101',
        'time': int(time.time()),
        'netstat': 'wifi',
        'device_id': get_random_id(32, 'device'),
        'bit_rate_type': rate,
        'protocol': 5,
    }
    params['sign'] = gsign(params)
    return get_response('https://m-glider-xiu.pps.tv/v2/stream/get.json',
                        data=params).json()

class PPS(Extractor):
    name = '奇秀（Qixiu)'

    rate_2_id_profile = {
        'source': ['TD', '超清'],
          'high': ['HD', '高清'],
        'smooth': ['SD', '标清']
    }

    def prepare_mid(self):
        html = get_content(self.url)
        return match1(html, '"user_id":"([^"]+)",')

    def prepare(self):
        info = MediaInfo(self.name, True)

        html = get_content(self.url)
        title = json.loads(match1(html, '"room_name":("[^"]*"),'))
        artist = json.loads(match1(html, '"nick_name":("[^"]+"),'))
        info.title = '{title} - {artist}'.format(**vars())
        info.artist = artist

        def get_live_info(rate='source'):
            data = getlive(self.mid, rate)
            if data['code'] != 'A00000':
                return data.get('msg')

            data = data['data']
            url = data.get('https_flv') or data.get('flv') or data.get('rtmp')
            if url:
                url = url.replace('rtmp://', 'http://')
                ran = random.randrange(1e4)
                sep = '?' in url and '&' or '?'
                url = '{url}{sep}ran={ran}'.format(**vars())
                stream_id, stream_profile = self.rate_2_id_profile[rate]
                info.streams[stream_id] = {
                    'container': 'flv',
                    'profile': stream_profile,
                    'src' : [url],
                    'size': Infinity
                }

            error_msges = []
            if rate == 'source':
                rate_list = data['rate_list']
                if 'source' in rate_list:
                    rate_list.remove('source')
                    for rate in rate_list:
                        error_msg = get_live_info(rate)
                        if error_msg:
                            error_msges.append(error_msg)
            if error_msges:
                return ', '.join(error_msges)

        error_msg = get_live_info()
        if error_msg:
            self.logger.debug('error_msg:\n\t' + error_msg)

        return info

site = PPS()
