#!/usr/bin/env python

from ..util.html import get_content
from ..util.match import match1
from ..extractor import VideoExtractor
from ..common import playlist_not_supported

from random import randint
import json

class Hunantv(VideoExtractor):
    name = "芒果TV (HunanTV)"

    supported_stream_types = [ '超清', '高清', '标清' ]

    def prepare(self, **kwargs):
        assert self.url or self.vid

        if self.url and not self.vid:
            self.vid = match1(self.url, "/([0-9]+).html")

        rn = randint(0, 99999999)
        api_url = 'http://v.api.hunantv.com/player/video?video_id={}&random={}'.format(self.vid,rn)
        meta = json.loads(get_content(api_url))

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
        if self.param.info_only:
            for stream in self.stream_types:
                meta = json.loads(get_content(self.streams[stream]['url']))
                self.streams[stream]['src'] = [meta['info']]
                self.streams[stream]['size'] = 0
            return
        else:
            stream_id = self.param.stream_id or self.stream_types[0]

        meta = json.loads(get_content(self.streams[stream_id]['url']))
        self.streams[stream_id]['src'] = [meta['info']]
        self.streams[stream_id]['size'] = 0

site = Hunantv()
download = site.download_by_url
download_playlist = playlist_not_supported('hunantv')
