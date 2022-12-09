# -*- coding: utf-8 -*-

from .._common import *


class NeteaseLive(Extractor):
    name = '网易CC直播 (163)'

    profile_2_id = {
        '原画': 'OG',
        '蓝光': 'BD',
        '超清': 'TD',
        '高清': 'HD',
        '标清': 'SD',
    }

    quality_2_profile = {
     'blueray': '蓝光',
       'ultra': '超清',
        'high': '高清',
    'standard': '标清',
    }

    def prepare_mid(self):
        return match1(self.url, '\D/(\d+)/?$')

    def prepare(self):
        info = MediaInfo(self.name, True)

        html = get_content(self.url, headers={'Referer': 'https://cc.163.com/'})
        data = match1(html, '<script id="__NEXT_DATA__".*?>(.*?)</script>')
        #self.logger.debug('data:\n%s', data)  # too long
        data = json.loads(data)

        def get_live_info(vbr=0):
            params = vbr and {'vbr': vbr} or None
            data = get_response('http://cgi.v.cc.163.com/video_play_url/{self.mid}'
                                .format(**vars()), params=params).json()

            stream_profile = data['vbrname_mapping'][data['pc_vbr_sel']]
            stream_id = self.profile_2_id[stream_profile]
            info.streams[stream_id] = {
                'container': 'flv',
                'profile': stream_profile,
                'src' : [data['videourl']],
                'size': Infinity
            }

            if vbr == 0:
                vbr_sel = data['vbr_sel']
                for vbr in data['vbr_list']:
                    if vbr != vbr_sel:
                        get_live_info(vbr)

        try:
            # project, select first living room
            data = data['props']['pageProps']['data']
            rooms = data['module_infos'][0]['content']

        except KeyError:
            data = data['props']['pageProps']['roomInfoInitData']
            assert 'micfirst' in data, 'unsupported live!'

            info.title = data['live']['title']
            info.artist = data['micfirst']['nickname']

            try:
                streams = data['live']['quickplay']['resolution']
            except KeyError:
                get_live_info()
            else:
                for quality, stream in streams.items():
                    stream_profile = self.quality_2_profile[quality]
                    stream_id = self.profile_2_id[stream_profile]
                    cdn = stream['cdn']
                    cdn.pop('wy', None)  # UDP
                    url = random.choice(list(cdn.values()))
                    info.streams[stream_id] = {
                        'container': 'flv',
                        'profile': stream_profile,
                        'src' : [url],
                        'size': Infinity
                    }

        else:
            for room in rooms:
                if room['is_living']:
                    self.mid = room['ccid']
                    info.artist = room['name']
                    break
            info.title = data['share_title']
            get_live_info()

        return info

site = NeteaseLive()
