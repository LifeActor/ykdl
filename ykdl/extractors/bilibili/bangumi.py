# -*- coding: utf-8 -*-

from .._common import *
from .util import *
from .bilibase import BiliBase


APPKEY = '84956560bc028eb7'
SECRETKEY = '94aba54af9065f71de72f5508f1cd42e'
api_url = 'https://bangumi.bilibili.com/player/web_api/v2/playurl'

ua_legacy = 'Mozilla/5.0 (X11; Linux x86_64; rv:50.1) Gecko/20100101 Firefox/50.1'

class BiliBan(BiliBase):
    name = '哔哩哔哩 番剧 (Bilibili Bangumi)'

    def list_only(self):
        return '/play/ss' in self.url

    def get_page_info(self, info):
        html = get_content(self.url, headers={'User-Agent': ua_legacy})
        data = json.loads(match1(html, '__INITIAL_STATE__=({.+?});'))

        epInfo = data['epInfo']
        assert epInfo['epStatus'] != 13, "can't play VIP video!"

        self.mid = epInfo['cid']
        mediaInfo = data['mediaInfo']
        self.seasonType = mediaInfo['ssType']
        ssTypeFormat = mediaInfo['ssTypeFormat']
        ss_name = ssTypeFormat['name']
        ss_name_e = ssTypeFormat['homeLink'].split('/')[-2].title()
        if ss_name_e != 'Anime':
            if ss_name_e == 'Tv':
                ss_name_e = 'TV'
            info.site = '哔哩哔哩 {ss_name} (Bilibili {ss_name_e})'.format(**vars())

        def get_badge():
            stype = epInfo['sectionType']
            if stype:
                for s in data['sections']:
                    if s['type'] == stype:
                        return s['title']
            else:
                return epInfo['badge']

        title_h1 = data['h1Title']
        title_share = epInfo['share_copy']
        title = title_h1 in title_share and title_share or title_h1
        badge = get_badge()
        if badge != '预告':
            badge = ''
        info.title = '{title} {badge}'.format(**vars())
        info.artist = mediaInfo.get('upInfo', {}).get('name') or \
                      mediaInfo.get('up_info', {}).get('uname')
        info.duration = epInfo['duration'] // 1000

    def get_api_url(self, qn):
        params = {
            'appkey': APPKEY,
            'cid': self.mid,
            'module': 'bangumi',
            'platform': 'html5',
            'player': 1,
            'qn': qn,
            'season_type': self.seasonType
        }
        return sign_api_url(api_url, params, SECRETKEY)

    def prepare_list(self):
        html = get_content(self.url, headers={'User-Agent': ua_legacy})
        data = json.loads(match1(html, '__INITIAL_STATE__=({.+?});'))
        epid = data['epInfo']['id']
        eplist = sum((s['epList'] for s in data['sections']), data['epList'])
        epids = [ep['id'] for ep in eplist if ep['epStatus'] != 13]

        skiped = len(eplist) - len(epids)
        if skiped:
            self.logger.info('skiped %d VIP videos', skiped)
        assert epids, "can't play VIP videos!"

        self.set_index(epid, epids)
        for id in epids:
            yield 'https://www.bilibili.com/bangumi/play/ep{id}'.format(**vars())

site = BiliBan()
