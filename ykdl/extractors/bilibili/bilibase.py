# -*- coding: utf-8 -*-

from .._common import *


class BiliBase(Extractor):
    format_2_type_profile = {
        'hdflv2': ('4K', '超清 4K'),       #120 IGNORE
       'flv_p60': ('BD', '高清 1080P60'),  #116 IGNORE
           'flv': ('BD', '高清 1080P'),    #80
    'flv720_p60': ('TD', '高清 720P'),     #74  IGNORE
        'flv720': ('TD', '高清 720P'),     #64
         'hdmp4': ('TD', '高清 720P'),     #48
        'flv480': ('HD', '清晰 480P'),     #32
           'mp4': ('SD', '流畅 360P'),     #16
        'flv360': ('SD', '流畅 360P'),     #15
        }

    def prepare(self):
        info = MediaInfo(self.name)
        info.extra.referer = 'https://www.bilibili.com/'
        info.extra['ua'] = fake_headers['User-Agent']

        self.get_page_info(info)

        def get_video_info(qn=0):
            # need login with high qn
            if qn == 74 or qn > 80:
                return

            api_url = self.get_api_url(qn)
            data = get_response(api_url).xml()['root']
            assert data['result'] == 'suee', '{}: {}, {}'.format(
                                  data['result'], data['code'], data['message'])

            durl = data['durl']
            urls = []
            size = 0
            for d in durl:
                urls.append(d['url'])
                size += d['size']
            fmt = data['format']
            if 'mp4' in fmt:
                ext = 'mp4'
            elif 'flv' in fmt:
                ext = 'flv'
            st, prf = self.format_2_type_profile[fmt]
            if urls:
                st += '-' + str(data['quality'])
                info.streams[st] = {
                    'container': ext,
                    'profile': prf,
                    'src' : urls,
                    'size': size
                }

            if qn == 0:
                aqlts = data['accept_quality'].split(',')
                aqlts.remove(str(data['quality']))
                for aqlt in aqlts:
                    get_video_info(int(aqlt))

        get_video_info()

        assert info.streams, "can't play this video!!"
        return info
