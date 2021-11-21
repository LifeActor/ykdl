# -*- coding: utf-8 -*-

from .._common import *


def sign_api_url(api_url, params_str, skey):
    sign = hash.md5(params_str + skey)
    return '{api_url}?{params_str}&sign={sign}'.format(**vars())

class BiliBase(VideoExtractor):
    format_2_type_profile = {
       'flv_p60': ('BD', '高清 1080P'),  #116 IGNORE
        'hdflv2': ('BD', '高清 1080P+'), #112 IGNORE
           'flv': ('BD', '高清 1080P'),  #80
    'flv720_p60': ('TD', '高清 720P'),   #74  IGNORE
        'flv720': ('TD', '高清 720P'),   #64
         'hdmp4': ('TD', '高清 720P'),   #48
        'flv480': ('HD', '清晰 480P'),   #32
           'mp4': ('SD', '流畅 360P'),   #16
        'flv360': ('SD', '流畅 360P'),   #15
        }

    def prepare(self):
        info = VideoInfo(self.name)
        info.extra['referer'] = 'https://www.bilibili.com/'
        info.extra['ua'] = fake_headers['User-Agent']

        self.vid, info.title, info.artist = self.get_page_info()

        assert self.vid, "can't play this video: " + self.url

        def get_video_info(qn=0):
            # need login with high qn
            if qn == 74 or qn > 80:
                return

            api_url = self.get_api_url(qn)
            resp = get_response(api_url)
            code = match1(resp, '<code>([^<])')
            if code:
                self.logger.debug('Error:\n', resp.text)
                return

            data = resp.xml()['video']
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
            if urls and st not in info.streams:
                info.stream_types.append(st)
                info.streams[st] = {
                    'container': ext,
                    'video_profile': prf,
                    'src' : urls,
                    'size': size
                }

            if qn == 0:
                aqlts = list(map(int, data['accept_quality'].split(',')))
                aqlts.remove(data['quality'])
                for aqlt in aqlts:
                    get_video_info(aqlt)

        get_video_info()

        assert len(info.stream_types), "can't play this video!!"
        return info
