# -*- coding: utf-8 -*-

from .._common import *
from .acbase import AcBase


class AcBan(AcBase):

    name = 'AcFun 弹幕视频网 (番剧)'

    def get_page_info(self, html):
        artist = None
        bgmInfo = json.loads(match1(html, '(?:pageInfo|bangumiData) = ({.+?});'))
        videoInfo = bgmInfo.get('currentVideoInfo')
        assert videoInfo, bgmInfo.get('playErrorMessage') or "can't play this video!!"

        title = '{} - {}'.format(bgmInfo['bangumiTitle'], bgmInfo['episodeName'])
        sourceVid = videoInfo['id']
        m3u8Info = videoInfo.get('playInfos')
        if m3u8Info:
            m3u8Info = m3u8Info[0]
        else:
            m3u8Info = videoInfo.get('ksPlayJson')

        return title, artist, sourceVid, m3u8Info

    def format_mid(self, mid):
        if not isinstance(mid, tuple):
            mid = mid, None
        mid = mid[:2]
        if len(mid) == 1:
            mid += (None, )
        bid, iid = mid
        assert fullmatch(bid, '(aa)?\d+')
        assert not iid or fullmatch(iid, '\d+_\d+')
        bid = match1(bid, '(\d+)')
        if self.url is None:
            if iid:
                self.url = 'https://www.acfun.cn/bangumi/aa{bid}_{iid}'.format(**vars())
            else:
                self.url = 'https://www.acfun.cn/bangumi/aa{bid}'.format(**vars())
        return mid

    def prepare_mid(self):
        mid = matchm(self.url, '/aa(\d+)_(\d+_\d+)', '/aa(\d+)')
        if mid[0]:
            return mid

    def list_only(self):
        bid, iid = self.mid
        return bid and not iid

    def prepare_list(self):
        bid, iid = self.mid
        html = get_content(
            'https://www.acfun.cn/bangumi/aa{bid}'.format(**vars()),
            params={
                'pagelets': 'pagelet_partlist',
                'reqID': 0,
                'ajaxpipe': 1,
                't': int(time.time() * 1000)
            })
        iids = matchall(html, '{bid}_(\d+_\d+)'.format(**vars()))
        self.set_index(iid, iids)
        for iid in iids:
            yield 'https://www.acfun.cn/bangumi/aa{bid}_{iid}'.format(**vars())

site = AcBan()
