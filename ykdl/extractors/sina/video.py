# -*- coding: utf-8 -*-

from .._common import *


def get_realurl(url, vid):
    params = urlencode({'vid': vid})
    url = '{url}?{params}'.format(**vars())
    if get_location(url) != url:
        return url  # redirect url will be expired, keep origin
    html = get_content(url)
    print(html)
    return matchall(html, 'CDATA\[([^\]]+)')[1]

class Sina(Extractor):
    name = '新浪视频 (sina)'

    def prepare_mid(self):
        mid = match1(self.url, 'video_id=(\d+)', '(\d{5,})\.swf')
        if mid:
            return mid
        html = get_content(self.url)
        return match1(html, '[vV]ideo_?[iI]d[\'"]?\s*[:=]\s*[\'"]?(\d+)')

    def prepare(self):
        info = MediaInfo(self.name)

        data = get_response('https://s.video.sina.com.cn/video/h5play',
                            params={'video_id': self.mid}).json()
        assert data['code'] == 1, data['message']
        data = data['data']

        info.title = data['title']
        info.duration = int(data['length']) // 1000

        for t in ['mp4', 'flv', 'hlv', '3gp']:
            video_info = data['videos'].get(t)
            if video_info:
                break

        for profile in video_info:
            v = video_info[profile]
            url = get_realurl(v['file_api'], v['file_id'])
            info.streams[profile] = {
                'container': v['type'],
                'profile': profile,
                'src': [url]
            }

        return info

    def prepare_list(self):
        html = get_content(self.url)
        return matchall(html, 'video_id: ([^,]+)')

site = Sina()
