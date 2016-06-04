#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.html import get_content, fake_headers
from ..util.match import match1, matchall
from .youkubase import YoukuBase
from .youkujs import install_acode
from ykdl.compact import HTTPSHandler, build_opener, HTTPCookieProcessor, install_opener

import time
import json
import ssl


youku_headers = fake_headers
youku_headers['Referer'] = 'v.youku.com'

class Youku(YoukuBase):
    name = u"优酷 (Youku)"

    ct = 12

    def download_playlist(self, url, param):
        self.url = url

        try:
            playlist_id = match1(self.url, 'youku\.com/playlist_show/id_([a-zA-Z0-9=]+)')
            assert playlist_id

            video_page = get_content('http://www.youku.com/playlist_show/id_%s' % playlist_id, headers=youku_headers)
            videos = matchall(video_page, ['a href="(http://v\.youku\.com/[^?"]+)'])

            for extra_page_url in matchall(video_page, ['href="(http://www\.youku\.com/playlist_show/id_%s_[^?"]+)' % playlist_id]):
                extra_page = get_content(extra_page_url, headers=youku_headers)
                videos += matchall(extra_page, ['a href="(http://v\.youku\.com/[^?"]+)'])

        except:
            video_page = get_content(url, headers=youku_headers)
            videos = videos = matchall(video_page, ['a href="(http://v\.youku\.com/[^?"]+)'])

        for video in videos:
            self.download(video, param)

    def setup(self):
        # Hot-plug cookie handler
        ssl_context = HTTPSHandler(
            context=ssl.SSLContext(ssl.PROTOCOL_TLSv1))
        cookie_handler = HTTPCookieProcessor()
        opener = build_opener(ssl_context, cookie_handler)
        opener.addheaders = [('Cookie','__ysuid=%d' % time.time())]
        install_opener(opener)



        install_acode('4', '1', 'b4et', 'boa4', 'o0b', 'poz')
        if self.url and not self.vid:
             self.vid = match1(self.url, 'youku\.com/v_show/id_([a-zA-Z0-9=]+)' ,\
                                         'player\.youku\.com/player\.php/sid/([a-zA-Z0-9=]+)/v\.swf',\
                                         'loader\.swf\?VideoIDS=([a-zA-Z0-9=]+)',\
                                         'loader\.swf\?VideoIDS=([a-zA-Z0-9=]+)',\
                                         'player\.youku\.com/embed/([a-zA-Z0-9=]+)')

        api_url = 'http://play.youku.com/play/get.json?vid=%s&ct=12' % self.vid
        api_url1 = 'http://play.youku.com/play/get.json?vid=%s&ct=10' % self.vid
        try:
            meta = json.loads(get_content(api_url, headers=youku_headers))
            meta1 = json.loads(get_content(api_url1, headers=youku_headers))
            data = meta['data']
            data1 = meta1['data']
            assert 'stream' in data1
        except:
            if 'error' in data1:
                if data1['error']['code'] == -202:
                    # Password protected
                    self.password_protected = True
                    self.password = input(log.sprint('Password: ', log.YELLOW))
                    api_url += '&pwd={}'.format(self.password)
                    api_url1 += '&pwd={}'.format(self.password)
                    meta1 = json.loads(get_content(api_url1, headers=youku_headers))
                    meta = json.loads(get_content(api_url, headers=youku_headers))
                    data1 = meta1['data']
                    data = meta['data']
                else:
                    raise AssertionError('[Failed] ' + data1['error']['note'])
            else:
                raise AssertionError('[Failed] Video not found.')

        self.title = data['video']['title']
        self.ep = data['security']['encrypt_string']
        self.ip = data['security']['ip']
        self.stream_data = data1['stream']

site = Youku()
