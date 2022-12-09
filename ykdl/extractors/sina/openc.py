# -*- coding: utf-8 -*-

from .._common import *


def get_k(vid, rand):
    t = str(int(time.time()) >> 6)
    s = '{vid}Z6prk18aWxP278cVAH{t}{rand}'.format(**vars())
    return hash.md5(s)[:16] + t

class OpenC(Extractor):
    name = 'Sina openCourse (新浪公开课)'

    def format_mid(self, mid):
        # [0] course id
        # [1] lesson id
        if not isinstance(mid, tuple):
            mid = mid, None
        mid = mid[:2]
        if len(mid) == 1:
            mid += (None, )
        cid, lid = mid
        cid = fullmatch(cid, '\d+')
        lid = fullmatch(lid, '\d+')
        assert cid
        return cid, lid

    def prepare_mid(self):
        mid = matchm(self.url, '/course/id_(\d+)/lesson_(\d+)',
                               '/course/id_(\d+)')
        if mid[0]:
            return mid

    def list_only(self):
        return not self.mid[1]

    def prepare(self):
        info = MediaInfo(self.name)

        cid, lid = self.mid
        if lid is None:
            url = 'https://open.sina.com.cn/course/id_{cid}/'
        else:
            url = 'https://open.sina.com.cn/course/id_{cid}/lesson_{lid}/'
        html = get_content(url.format(**vars()))
        vid = match1(html, 'playVideo\("(\d+)')
        info.artist = match1(html, '讲师：(.+?)<br/>')

        assert vid, "can't find vid!"

        rand = str(random.random())[:18]
        data = get_response('http://ask.ivideo.sina.com.cn/v_play.php',
                            params={
                               'vid': vid,
                               'ran': rand,
                               'p': 'i',
                               'k': get_k(vid, rand),
                            }).xml()['root']

        info.title = data['vname']
        urls = []
        size = 0
        for durl in data['durl']:
            urls.append(durl['url'])
            size += durl['filesize']

        info.streams['current'] = {
            'container': 'hlv',
            'profile': 'current',
            'src' : urls,
            'size': size
        }
        return info

    def prepare_list(self):
        cid, lid = self.mid
        url = 'https://open.sina.com.cn/course/id_{cid}/'
        html = get_content(url.format(**vars()))
        lids = [None] + matchall(html, '/lesson_(\d+)/">')
        self.set_index(lid, lids)
        for lid in lids:
            yield cid, lid

site = OpenC()
