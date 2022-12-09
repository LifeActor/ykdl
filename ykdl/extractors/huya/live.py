# -*- coding: utf-8 -*-

from .._common import *


class HuyaLive(Extractor):
    name = 'Huya Live (虎牙直播)'

    def profile_2_id(self, profile):
        if profile[-1] == 'M':
            return profile.replace('蓝光', 'BD')
        else:
            return {
                '蓝光': 'BD',
                '超清': 'TD',
                '高清': 'HD',
                '流畅': 'SD'
            }[profile]

    def prepare(self):
        info = MediaInfo(self.name, True)

        html  = get_content(self.url)

        data = match1(html, 'stream: ({.+)\n.*?};')
        assert data, "can't found video!!"
        self.logger.debug('data:\n%s', data)
        data = json.loads(data)
        assert data['vMultiStreamInfo'], 'live video is offline'

        room_info = data['data'][0]['gameLiveInfo']
        info.title = '{}「{} - {}」'.format(
            room_info['roomName'], room_info['nick'], room_info['introduction'])
        info.artist = room_info['nick']
        screenType = room_info['screenType']
        liveSourceType = room_info['liveSourceType']

        stream_info_list = data['data'][0]['gameStreamInfoList']
        random.shuffle(stream_info_list)
        random.shuffle(stream_info_list)
        while stream_info_list:
            stream_info = stream_info_list.pop()
            sUrl = stream_info['sFlvUrl']
            if sUrl:
                break
        sStreamName = stream_info['sStreamName']
        sUrlSuffix = stream_info['sFlvUrlSuffix']
        _url = '{sUrl}/{sStreamName}.{sUrlSuffix}?'.format(**vars())

        reSecret = not screenType and liveSourceType in (0, 8, 13)
        params = dict(parse_qsl(unescape(stream_info['sFlvAntiCode'])))
        if reSecret:
            params.setdefault('t', '100')  # 102
            ct = int((int(params['wsTime'], 16) + random.random()) * 1000)
            lPresenterUid = stream_info['lPresenterUid']
            if liveSourceType and not sStreamName.startswith(str(lPresenterUid)):
                uid = lPresenterUid
            else:
                uid = int(ct % 1e10 * 1e3 % 0xffffffff)
            u1 = uid & 0xffffffff00000000
            u2 = uid & 0xffffffff
            u3 = uid & 0xffffff
            u = u1 | u2 >> 24 | u3 << 8
            params.update({
                 'u': str(u),
                 'seqid': str(ct + uid),
                 'ver': '1',
                 'uuid': int((ct % 1e10 + random.random()) * 1e3 % 0xffffffff),
             })
            fm = unb64(params['fm']).split('_', 1)[0]
            ss = hash.md5('|'.join([params['seqid'], params['ctype'], params['t']]))

        for si in data['vMultiStreamInfo']:
            stream_profile = si['sDisplayName']
            stream_id = self.profile_2_id(stream_profile)
            rate = si['iBitRate']
            if rate:
                params['ratio'] = rate
            else:
                params.pop('ratio', None)
            if reSecret:
                params['wsSecret'] = hash.md5('_'.join(
                            [fm, params['u'], sStreamName, ss, params['wsTime']]))
            url = _url + urlencode(params, safe=',*')
            info.streams[stream_id] = {
                'container': 'flv',
                'profile': stream_profile,
                'src': [url],
                'size': Infinity
            }
        fake_headers.update({
            'Accept': '*/*',
            'Origin': 'https://www.huya.com',
            'Referer': 'https://www.huya.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
        })
        info.extra['header'] = fake_headers
        return info

site = HuyaLive()
