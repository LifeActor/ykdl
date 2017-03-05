#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.util.html import get_content
from ykdl.util.match import match1, matchall
from ykdl.compact import compact_bytes

import hashlib
import re
import json

appkey='f3bb208b3d081dc8'
SECRETKEY_MINILOADER = '1c15888dc316e05a15fdd0a02ed6584f'

def parse_cid_playurl(xml):
    from xml.dom.minidom import parseString
    urls = []
    size = 0
    doc = parseString(xml.encode('utf-8'))
    for durl in doc.getElementsByTagName('durl'):
        urls.append(durl.getElementsByTagName('url')[0].firstChild.nodeValue)
        size += int(durl.getElementsByTagName('size')[0].firstChild.nodeValue)
    return urls, size

class BiliVideo(VideoExtractor):
    name = u'哔哩哔哩 (Bilibili)'
    supported_stream_profile = [u'超清', u'高清', u'流畅']
    profile_2_type = {u'超清': 'TD', u'高清': 'HD', u'流畅' :'SD'}
    def prepare(self):
        info = VideoInfo(self.name)
        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, 'cid=(\d+)', 'cid=\"(\d+)')
            info.title = match1(html, '<title>([^<]+)').split("_")[0].strip(u" 番剧 bilibili 哔哩哔哩弹幕视频网")
            if not self.vid:
                eid = match1(self.url, 'anime/v/(\d+)', 'play#(\d+)') or match1(html, 'anime/v/(\d+)')
                if eid:
                    Episode_info = json.loads(get_content('http://bangumi.bilibili.com/web_api/episode/{}.json'.format(eid)))['result']['currentEpisode']
                    self.vid = Episode_info['danmaku']
                    info.title = info.title + ' ' + Episode_info['index'] + '.  ' + Episode_info['longTitle']

        assert self.vid, "can't play this video: {}".format(self.url)
        for q in self.supported_stream_profile:
            sign_this = hashlib.md5(compact_bytes('cid={}&from=miniplay&player=1&quality={}{}'.format(self.vid, 3-self.supported_stream_profile.index(q), SECRETKEY_MINILOADER), 'utf-8')).hexdigest()
            api_url = 'http://interface.bilibili.com/playurl?cid={}&player=1&quality={}&from=miniplay&sign={}'.format(self.vid, 3-self.supported_stream_profile.index(q), sign_this)
            html = get_content(api_url)
            urls, size = parse_cid_playurl(html)
            ext = 'flv'

            info.stream_types.append(self.profile_2_type[q])
            info.streams[self.profile_2_type[q]] = {'container': ext, 'video_profile': q, 'src' : urls, 'size': size}
        return info

    def prepare_list(self):
        html = get_content(self.url)
        video_list = matchall(html, ['<option value=\'([^\']*)\''])
        if video_list:
            return ['http://www.bilibili.com'+v for v in video_list]
        sid = match1(html, 'var season_id = "(\d+)";')
        j_ = get_content("http://bangumi.bilibili.com/jsonp/seasoninfo/{}.ver".format(sid))
        s_data = json.loads(j_)
        urls = [e['webplay_url'] for e in sorted(s_data['result']['episodes'], key=lambda e: e['index'])]
        return urls

site = BiliVideo()
