# -*- coding: utf-8 -*-

from .._common import *


def get_k(vid, rand):
    t = str(int(time.time()) >> 6)
    s = '{vid}Z6prk18aWxP278cVAH{t}{rand}'.format(**vars())
    return hash.md5(s)[:16] + t

class OpenC(Extractor):
    name = 'Sina openCourse (新浪公开课)'

    def prepare(self):
        info = MediaInfo(self.name)

        if self.url:
            html = get_content(self.url)
            self.vid = match1(html, 'playVideo\("(\d+)')
            info.artist = match1(html, '讲师：(.+?)<br/>')

        self.logger.debug('VID: %s', self.vid)

        rand = str(random.random())[:18]
        data = get_response('http://ask.ivideo.sina.com.cn/v_play.php',
                            params={
                               'vid': self.vid,
                               'ran': rand,
                               'p': 'i',
                               'k': get_k(self.vid, rand),
                            }).xml()['root']

        info.title = data['vname']
        urls = []
        size = 0
        for durl in data['durl']:
            urls.append(durl['url'])
            size += durl['filesize']

        info.streams['current'] = {
            'container': 'hlv',
            'video_profile': 'current',
            'src': urls,
            'size': size
        }
        return info

site = OpenC()
