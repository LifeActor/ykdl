#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.html import get_content, parse_query_param
from ..util.match import match1, matchall
from ..util import log
from ..extractor import VideoExtractor
from .youkujs import *

import base64
import time
import traceback
import urllib.parse
import math
import json

class Youku(VideoExtractor):
    name = "优酷 (Youku)"

    # Last updated: 2015-11-24
    supported_stream_code = [ 'mp4hd3', 'hd3', 'mp4hd2', 'hd2', 'mp4hd', 'mp4', 'flvhd', 'flv', '3gphd' ]
    stream_code_to_type = {
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
    stream_code_to_profiles = {
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
    stream_type_to_container = {
         'hd3' : 'flv',
         'hd2' : 'flv',
         'mp4' : 'mp4',
         'flvhd': 'flv',
         'flv' : 'flv',
         '3gphd': 'mp4'
    }

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
            videos = videos = matchall(video_page, ['a href="(http://v\.youku\.com/[^?"]+)'])

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
        self.streams_parameter = {}
        assert self.url or self.vid

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
            assert 'stream' in data
        except:
            if 'error' in data:
                if data['error']['code'] == -202:
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
                    log.wtf('[Failed] ' + data['error']['note'])
            else:
                log.wtf('[Failed] Video not found.')

        self.title = data['video']['title']
        self.ep = data['security']['encrypt_string']
        self.ip = data['security']['ip']

        stream_types = dict([(i['id'], i) for i in self.stream_types])

        for stream in data1['stream']:
            stream_id = stream['stream_type']
            if not stream_id in self.stream_types:
                self.streams_parameter[stream_id] = {
                    'fileid': stream['stream_fileid'],
                    'segs': stream['segs']
                }
                self.streams[stream_id] = {
                    'container': self.stream_type_to_container[self.stream_code_to_type[stream_id]],
                    'video_profile': self.stream_code_to_profiles[stream_id],
                    'size': stream['size']
                }
                self.stream_types.append(stream_id)


        # Audio languages
        if 'dvd' in data and 'audiolang' in data['dvd']:
            self.audiolang = data['dvd']['audiolang']
            for i in self.audiolang:
                i['url'] = 'http://v.youku.com/v_show/id_{}'.format(i['vid'])

        self.stream_types = sorted(self.stream_types, key = self.supported_stream_code.index)


    def extract(self, **kwargs):
        stream_id = self.param.stream_id or self.stream_types[0]
        sid, token = init(self.ep)
        segs = self.streams_parameter[stream_id]['segs']
        streamfileid = self.streams_parameter[stream_id]['fileid']
        urls = []
        no = 0
        for seg in segs:
            k = seg['key']
            if k == -1:
                log.e('Error')
                exit()
            fileId = getFileid(streamfileid, no)
            ep  = urllib.parse.quote(create_ep(sid, fileId, token), safe='~()*!.\'')
            if no < 10:
                nu = '0'+str(no)
            else:
                nu = str(no)
            m3u8 = ''
            m3u8  += 'http://k.youku.com/player/getFlvPath/sid/'+ sid + '_' + nu
            m3u8+= '/st/'+ self.streams[stream_id]['container']
            m3u8+='/fileid/'+ fileId
            m3u8+='?K='+ k
            m3u8+='&ctype=12&ev=1&token='+ token
            m3u8+='&oip='+ str(self.ip)
            m3u8+='&ep='+ ep
            no += 1
            urls.append(m3u8)

        if not self.param.info_only:
            self.streams[stream_id]['src'] = urls
            if not self.streams[stream_id]['src'] and self.password_protected:
                log.e('[Failed] Wrong password.')

site = Youku()
download = site.download_by_url
download_playlist = site.download_playlist_by_url
