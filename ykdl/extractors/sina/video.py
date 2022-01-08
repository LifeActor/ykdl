# -*- coding: utf-8 -*-

from .._common import *


def get_realurl(url, vid):
    resp = get_response(url, params={'vid': vid})
    if resp.locations:
        return resp.url
    else:
       return matchall(resp, 'CDATA\[([^\]]+)')[1]

class Sina(Extractor):
    name = '新浪视频 (sina)'

    def prepare(self):
        info = MediaInfo(self.name)
        if not self.vid:
            self.vid = match1(self.url, 'video_id=(\d+)',
                                        '#(\d{5,})',
                                        '(\d{5,})\.swf')
            if not self.vid:
                html = get_content(self.url)
                self.vid = match1(html, 'video_id[\'"]?\s*[:=]\s*[\'"]?(\d+)')

        assert self.vid, "can't get vid"

        data = get_response('http://s.video.sina.com.cn/video/h5play',
                            params={'video_id': self.vid}).json()
        data = data['data']
        info.title = data['title']
        for t in ['mp4', 'flv', '3gp']:
            video_info = data['videos'].get(t)
            if video_info:
                break

        for profile in video_info:
            v = video_info[profile]
            r_url = get_realurl(v['file_api'], v['file_id'])
            info.streams[profile] = {
                'container': v['type'],
                'video_profile': profile,
                'src': [r_url],
                'size' : 0
            }
        return info

    def prepare_list(self):
        html = get_content(self.url)
        return matchall(html, 'video_id: ([^,]+)')

site = Sina()
