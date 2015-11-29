#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.html import get_content, parse_query_param
from ..util.match import match1, matchall
from ..extractor import VideoExtractor
from ..util import log

import base64
import time
import traceback
import json
from urllib import parse

class Youku(VideoExtractor):
    name = "优酷 (Youku)"

    # Last updated: 2015-11-24
    supported_stream_types = [ 'mp4hd3', 'hd3', 'mp4hd2', 'hd2', 'mp4hd', 'mp4', 'flvhd', 'flv', '3gphd' ]
    stream_alias = {
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
    stream_types_to_profiles = {
        'mp4hd3': '1080p',
        'hd3'   : '1080P',
        'mp4hd2': '超清',
        'hd2'   : '超清',
        'mp4hd' : '高清',
        'mp4'   : '高清',
        'flvhd' : '标清',
        'flv'   : '标清',
        '3gphd' : '标清（3GP）'
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

        api_url = 'http://play.youku.com/play/get.json?vid=%s&ct=12' % self.vid
        try:
            meta = json.loads(get_content(api_url))
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

        stream_types = dict([(i['id'], i) for i in self.stream_types])
        for stream in data['stream']:
            stream_id = stream['stream_type']
            if stream_id in self.supported_stream_types:
                self.streams[stream_id] = {
                    'container': 'mp4',
                    'video_profile': self.stream_types_to_profiles[stream_id],
                    'size': stream['size']
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
        new_ep, sid, token = self.__class__.generate_ep(self.vid, self.ep)
        m3u8_query = parse.urlencode(dict(
            ctype=12,
            ep=new_ep,
            ev=1,
            keyframe=1,
            oip=self.ip,
            sid=sid,
            token=token,
            ts=int(time.time()),
            type=self.stream_alias[stream_id],
            vid=self.vid,
        ))
        m3u8_url = 'http://pl.youku.com/playlist/m3u8?' + m3u8_query

        if not self.param.info_only:
            if self.password_protected:
                m3u8_url += '&password={}'.format(self.password)

            m3u8 = get_content(m3u8_url)
            print(m3u8)
            self.streams[stream_id]['src'] = matchall(m3u8, ['(http://[^?]+)\?ts_start=0'])
            if not self.streams[stream_id]['src'] and self.password_protected:
                log.e('[Failed] Wrong password.')

site = Youku()
download = site.download_by_url
download_playlist = site.download_playlist_by_url
