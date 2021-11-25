# -*- coding: utf-8 -*-

from .._common import *


def get_realurl(url, vid):
    resp = get_response(url, params={'vid': vid})
    if resp.locations:
        return resp.url
    else:
       return matchall(resp, 'CDATA\[([^\]]+)')[1]

class Sina(VideoExtractor):
    name = '新浪视频 (sina)'

    def prepare(self):
        info = VideoInfo(self.name)
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
        for t in ['mp4', '3gp', 'flv']:
            if t in data['videos']:
                video_info = data['videos'][t]
                break

        for profile in video_info:
            if not profile in info.stream_types:
                v = video_info[profile]
                r_url = get_realurl(v['file_api'], v['file_id'])
                info.stream_types.append(profile)
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
