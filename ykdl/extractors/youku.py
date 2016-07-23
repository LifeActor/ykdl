#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content, add_header
from ykdl.util.match import match1, matchall
from ykdl.util import log
from .youkubase import YoukuBase
from .youkujs import install_acode
from ykdl.compact import HTTPSHandler, build_opener, HTTPCookieProcessor, install_opener

import time
import json
import ssl

class Youku(YoukuBase):
    name = u"优酷 (Youku)"

    ct = 12

    def setup(self, info):
        # Hot-plug cookie handler
        ssl_context = HTTPSHandler(
            context=ssl.SSLContext(ssl.PROTOCOL_TLSv1))
        cookie_handler = HTTPCookieProcessor()
        opener = build_opener(ssl_context, cookie_handler)
        opener.addheaders = [('Cookie','__ysuid=%d' % time.time())]
        install_opener(opener)

        add_header('Referer', 'v.youku.com')

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
            meta = json.loads(get_content(api_url))
            meta1 = json.loads(get_content(api_url1))
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
                    meta1 = json.loads(get_content(api_url1))
                    meta = json.loads(get_content(api_url))
                    data1 = meta1['data']
                    data = meta['data']
                else:
                    raise AssertionError('[Failed] ' + data1['error']['note'])
            else:
                raise AssertionError('[Failed] Video not found.')

        info.title = data['video']['title']
        self.ep = data['security']['encrypt_string']
        self.ip = data['security']['ip']
        try:
            self.stream_data = data1['stream']
        except:
            if self.password_protected:
                raise AssertionError('incorrect password!!')
            else:
                raise AssertionError('No Stream found!!')

site = Youku()
