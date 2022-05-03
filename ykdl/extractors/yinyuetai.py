# -*- coding: utf-8 -*-

from ._common import *


class YinYueTai(Extractor):
    name = '音悦台 (YinYueTai)'

    def prepare(self):
        info = MediaInfo(self.name)
        info.extra.referer = 'https://www.yinyuetai.com/'
        if not self.vid:
            self.vid = match1(self.url,'\Wid=(\d+)')

        data = get_response('https://data.yinyuetai.com/video/getVideoInfo',
                            params={'id': self.vid}).json()
        assert not data['delFlag'], 'MTV has been deleted!'

        info.title = data['videoName']
        info.artist = data['artistName']

        url = data['videoUrl']
        info.streams['current'] = {
            'container': url_info(url)[1],
            'video_profile': 'current',
            'src' : [url]
        }

        return info

site = YinYueTai()
