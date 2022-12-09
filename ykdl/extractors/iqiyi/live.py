# -*- coding: utf-8 -*-

from .._common import *
from .util import cmd5x_iqiyi3 as cmd5x

# May be closed, see x.pps.tv


def getlive(vid):
    tm = time.time()
    host = 'https://live.video.iqiyi.com'
    dfp = get_random_id(66)
    params = {
        'lp': vid,
        'src': '01010031010000000000',
        'uid': '',
        'rateVers': 'PC_QIYI_3',
        'k_uid': get_random_id(24, 'k_uid'),
        'qdx': 'n',
        'qdv': 3,
        'qd_v': 1,
        'dfp': dfp,
        'v': 1,
        'k_err_retries': 0,
        'tm': int(tm + 1),
    }
    src = '/live?' + urlencode(params)
    vf = cmd5x(src)
    req_url = '{host}{src}&vf={vf}'.format(**vars())
    st = int(tm * 1000)
    et = int((tm + 1296000) * 1000)
    c_dfp = '__dfp={dfp}@{et}@{st}'.format(**vars())
    return get_response(req_url, {'Cookie': c_dfp}).json()

class IqiyiLive(Extractor):
    name = '爱奇艺直播 (IqiyiLive)'

    type_2_id = {
        #'': '4K',
        'RESOLUTION_1080P': 'BD',
        'RESOLUTION_720P': 'TD',
        'HIGH_DEFINITION': 'HD',
        'SMOOTH': 'SD',
        #'': 'LD'
    }

    def prepare_mid(self):
        html = get_content(self.url)
        return match1(html, '"qpId":(\d+)')

    def prepare(self):
        info = MediaInfo(self.name, True)

        data = getlive(self.mid)
        assert data['code'] == 'A00000', data.get('msg', "can't play this live video!")
        data = data['data']
        assert data['liveType'] != 2, 'this live is off!'
        info.title = data['name']

        for stream in data['streams']:
            stream_type = stream['steamType']  # typo 'streamType' to 'steamType'
            stream_id = self.type_2_id[stream_type]

            if stream['formatType'] == 'HLFLV':
                stream_params = stream['url'].split('?')[-1]
                stream_params_dict = dict(parse_qsl(stream_params))
                if stream_params_dict['hl_sttp'] != 'flv':
                    continue
                params = {
                    'streamName': stream['streamName'],
                    'streamParams': stream_params,
                    'hl_stid': stream_params_dict['hl_stid'],
                    'hl_stft': stream_params_dict['hl_stft'],
                    'hl_stapp': stream_params_dict['hl_stapp']
                }
                url = get_response('https://flvlive.video.iqiyi.com/{hl_stapp}/'
                                   '{streamName}.{hl_stft}?{streamParams}'
                                   .format(**params)).json()['l']
                url = url.replace('{streamName}.'.format(**params),
                                  '{hl_stid}.'.format(**params))
                ext = 'flv'
            elif stream_id in info.streams:
                continue
            elif stream['formatType'] == 'TS':
                url = stream['url']
                ext = 'm3u8'

            stream_profile = stream['screenSize']
            info.streams[stream_id] = {
                'container': ext,
                'profile': stream_profile,
                'src' : [url],
                'size': Infinity
            }

        return info

site = IqiyiLive()
