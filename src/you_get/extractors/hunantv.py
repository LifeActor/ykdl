#!/usr/bin/env python

from ..common import *
from ..extractor import VideoExtractor
from random import randint
import json
import re

class Hunantv(VideoExtractor):
    name = "芒果TV (HunanTV)"

    supported_stream_types = [ '超清', '高清', '标清' ]

    def prepare(self, **kwargs):
        assert self.url or self.vid

        if self.url and not self.vid:
            self.vid = match1(self.url, "/([0-9]+).html")

        rn = randint(0, 99999999)
        api_url = 'http://v.api.hunantv.com/player/video?video_id={}&random={}'.format(self.vid,rn)
        meta = json.loads(get_html(api_url))
        if meta['status'] != 200:
            log.wtf('[failed] status: {}, msg: {}'.format(meta['status'],meta['msg']))
        if not meta['data']:
            log.wtf('[Failed] Video not found.')
        data = meta['data']

        info = data['info']
        self.title = info['title']
        for stream in self.supported_stream_types:
            for lstream in data['stream']:
                if stream == lstream['name']:
                    break;
            self.streams[lstream['name']] = {'container': 'fhv', 'video_profile': lstream['name'], 'url' : lstream['url']}
            self.stream_types.append(lstream['name'])

    def extract(self, **kwargs):
        if 'info_only' in kwargs and kwargs['info_only']:
          for stream in self.stream_types:
                meta = ''
                while True:
                    rn = randint(0, 99999999)
                    meta = json.loads(get_html("{}&random={}".format((self.streams[stream]['url']),rn)))
                    if meta['status'] == 'ok':
                        if meta['info'].startswith('http://pcfastvideo.imgo.tv/'):
                            break
                size = url_size(meta['info'])
                self.streams[stream]['src'] = [meta['info']]
                self.streams[stream]['size'] = size
        else:

            if 'stream_id' in kwargs and kwargs['stream_id']:
                # Extract the stream
                stream_id = kwargs['stream_id']

                if stream_id not in self.streams:
                    log.e('[Error] Invalid video format.')
                    log.e('Run \'-i\' command with no specific video format to view all available formats.')
                    exit(2)
            else:
                # Extract stream with the best quality
                stream_id = self.stream_types[0]


            meta = ''
            while True:
                rn = randint(0, 99999999)
                meta = json.loads(get_html("{}&random={}".format((self.streams[stream_id]['url']),rn)))
                if meta['status'] == 'ok':
                    if meta['info'].startswith('http://pcfastvideo.imgo.tv/'):
                        break
            size = url_size(meta['info'])
            self.streams[stream_id]['src'] = [meta['info']]
            self.streams[stream_id]['size'] = size

site = Hunantv()
download = site.download_by_url
download_playlist = playlist_not_supported('hunantv')
