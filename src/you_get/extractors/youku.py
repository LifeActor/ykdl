#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.html import get_content, parse_query_param
from ..util.match import match1, matchall
from ..extractor import VideoExtractor
from ..util import log

from .youkujs import *

import base64
import time
import traceback
import json
from urllib import parse
import random

class Youku(VideoExtractor):
    name = "优酷 (Youku)"

    # Last updated: 2015-11-24
    supported_stream_types = [ 'mp4hd3', 'hd3', 'mp4hd2', 'hd2', 'mp4hd', 'mp4', 'flvhd', 'flv', '3gphd' ]
    stream_to_code = {
        'mp4hd3': 'hd3',
        'hd3'   : 'hd3',
        'mp4hd2': 'hd2',
        'hd2'   : 'hd2',
        'mp4hd' : 'mp4',
        'mp4'   : 'mp4',
        'flvhd' : 'flvhd',
        'flv'   : 'flv',
        '3gphd' : '3gphd'
    }
    code_to_profiles = {
        'hd3'   : '1080P',
        'hd2'   : '超清',
        'mp4'   : '高清',
        'flvhd' : '标清',
        'flv'   : '标清',
        '3gphd' : '标清（3GP）'
    }

    code_to_hd = {
        'hd3': 3,
        'hd2': 2,
        'mp4': 1,
        'flvhd': 1,
        'flv': 0,
        '3gphd': 0
    }

    code_to_container = {
      'flv': 'flv',
      'mp4': 'mp4',
      'hd2': 'flv',
      'mp4hd': 'mp4',
      'mp4hd2': 'mp4',
      '3gphd': 'mp4',
      '3gp': 'flv',
      'flvhd': 'flv',
      'hd3': 'flv'
    }

    def generate_ep(vid, ep):
        f_code_1 = 'becaf9be'
        f_code_2 = 'bf7e5f01'

        def trans_e(a, c):
            f = h = 0
            b = list(range(256))
            result = ''
            while h < 256:
                f = (f + b[h] + ord(a[h % len(a)])) % 256
                b[h], b[f] = b[f], b[h]
                h += 1
            q = f = h = 0
            while q < len(c):
                h = (h + 1) % 256
                f = (f + b[h]) % 256
                b[h], b[f] = b[f], b[h]
                if isinstance(c[q], int):
                    result += chr(c[q] ^ b[(b[h] + b[f]) % 256])
                else:
                    result += chr(ord(c[q]) ^ b[(b[h] + b[f]) % 256])
                q += 1

            return result

        e_code = trans_e(f_code_1, base64.b64decode(bytes(ep, 'ascii')))
        sid, token = e_code.split('_')
        new_ep = trans_e(f_code_2, '%s_%s_%s' % (sid, vid, token))
        return base64.b64encode(bytes(new_ep, 'latin')), sid, token

    def download_playlist_by_url(self, url, param,  **kwargs):
        self.url = url

        try:
            playlist_id = match1(self.url, 'youku\.com/playlist_show/id_([a-zA-Z0-9=]+)')
            assert playlist_id

            video_page = get_content('http://www.youku.com/playlist_show/id_%s' % playlist_id)
            videos = matchall(video_page, ['a href="(http://v\.youku\.com/[^?"]+)'])

            for extra_page_url in matchall(video_page, ['href="(http://www\.youku\.com/playlist_show/id_%s_[^?"]+)' % playlist_id]):
                extra_page = get_content(extra_page_url)
                videos += matchall(extra_page, ['a href="(http://v\.youku\.com/[^?"]+)'])

        except:
            video_page = get_content(url)
            videos = matchall(video_page, ['a href="(http://v\.youku\.com/[^?"]+)'])

        for video in videos:
            index = parse_query_param(video, 'f')
            try:
                self.download_by_url(video, param, **kwargs)
            except KeyboardInterrupt:
                raise
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback)

    def prepare(self, **kwargs):
        assert self.url or self.vid

        if self.url and not self.vid:
            self.vid = match1(self.url, 'youku\.com/v_show/id_([a-zA-Z0-9=]+)' ,\
                                        'player\.youku\.com/player\.php/sid/([a-zA-Z0-9=]+)/v\.swf',\
                                        'loader\.swf\?VideoIDS=([a-zA-Z0-9=]+)',\
                                        'loader\.swf\?VideoIDS=([a-zA-Z0-9=]+)',\
                                        'player\.youku\.com/embed/([a-zA-Z0-9=]+)')

            if self.vid is None:
                self.download_playlist_by_url(self.url, **kwargs)
                exit(0)

        api_url = 'http://play.youku.com/play/get.json?vid={}&ct=12&ran={}'.format(self.vid, random.randint(0,9999))
        try:
            content = get_content(api_url)
            meta = json.loads(content)
            data = meta['data']
            assert 'stream' in data
        except:
            if 'error' in data:
                if data['error']['code'] == -202:
                    # Password protected
                    self.password_protected = True
                    self.password = input(log.sprint('Password: ', log.YELLOW))
                    api_url += '&pwd={}'.format(self.password)
                    meta = json.loads(get_html(api_url))
                    data = meta['data']
                else:
                    log.wtf('[Failed] ' + data['error']['note'])
            else:
                log.wtf('[Failed] Video not found.')

        self.title = data['video']['title']
        self.ep = data['security']['encrypt_string']
        self.ip = data['security']['ip']
        for stream in data['stream']:
            stream_id = stream['stream_type']
            if stream_id in self.supported_stream_types:
                self.streams[stream_id] = {
                    'container': self.code_to_container[self.stream_to_code[stream_id]],
                    'video_profile': self.code_to_profiles[self.stream_to_code[stream_id]],
                    'size': stream['size'],
                    'segs': stream['segs'],
                    'stream_fileid': stream['stream_fileid'],
                    'hd' : self.code_to_hd[self.stream_to_code[stream_id]]
                }
                self.stream_types.append(stream_id)

        # Audio languages
        if 'dvd' in data and 'audiolang' in data['dvd']:
            self.audiolang = data['dvd']['audiolang']
            for i in self.audiolang:
                i['url'] = 'http://v.youku.com/v_show/id_{}'.format(i['vid'])

        self.stream_types = sorted(self.stream_types, key = self.supported_stream_types.index)

    def extract(self, **kwargs):
        stream_id = self.param.stream_id or self.stream_types[0]
        sid, token = init(self.ep)
        i = 0
        urls = []
        for seg in self.streams[stream_id]['segs']:
            index = '%02d' % i
            fileid = getFileid(self.streams[stream_id]['stream_fileid'], i)
            new_ep = create_ep(sid, fileid, token)
            ts = int(int(seg['total_milliseconds_video']) / 1000)
            seg_get_url = 'http://k.youku.com/player/getFlvPath/sid/{}_{}/st/{}/fileid/{}?K={}&hd={}&myp=0&ts={}&ymovie=1&ypp=0&ctype=12&ev=1&token={}&oip={}&ep={}&yxon=1&special=true'.format(sid, index, self.streams[stream_id]['container'], fileid, seg['key'], self.streams[stream_id]['hd'], ts, token, self.ip, new_ep)
            info = json.loads(get_content(seg_get_url))
            urls.append(info[0]['server'])
            i += 1
        self.streams[stream_id]['src'] = urls

site = Youku()
download = site.download_by_url
download_playlist = site.download_playlist_by_url
