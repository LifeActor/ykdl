#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.html import get_content
from ..util.match import match1, matchall
from ..extractor import VideoExtractor

from random import randint
import json

class Hunantv(VideoExtractor):
    name = u"芒果TV (HunanTV)"

    supported_stream_profile = [ u'超清', u'高清', u'标清' ]
    supported_stream_types = [ 'TD', 'HD', 'SD' ]
    profile_2_types = { u'超清': 'TD', u'高清': 'HD', u'标清': 'SD' }

    def prepare(self):

        if self.url and not self.vid:
            self.vid = match1(self.url, "/([0-9]+).html")

        rn = randint(0, 99999999)
        api_url = 'http://v.api.hunantv.com/player/video?video_id={}&random={}'.format(self.vid,rn)
        meta = json.loads(get_content(api_url))

        assert meta['status'] == 200, '[failed] status: {}, msg: {}'.format(meta['status'],meta['msg'])
        assert meta['data'], '[Failed] Video not found.'

        data = meta['data']

        info = data['info']
        self.title = info['title']
        for lstream in data['stream']:
            self.streams[self.profile_2_types[lstream['name']]] = {'container': 'm3u8', 'video_profile': lstream['name'], 'url' : lstream['url']}
            self.stream_types.append(self.profile_2_types[lstream['name']])
        self.stream_types= sorted(self.stream_types, key = self.supported_stream_types.index)

    def extract(self):
        if self.param.info:
            for stream in self.stream_types:
                meta = json.loads(get_content(self.streams[stream]['url']))
                self.streams[stream]['src'] = [meta['info']]
                self.streams[stream]['size'] = 0
            return
        else:
            stream_id = self.param.format or self.stream_types[0]

        meta = json.loads(get_content(self.streams[stream_id]['url']))
        self.streams[stream_id]['src'] = [meta['info']]
        self.streams[stream_id]['size'] = 0

    def prepare_list(self):

        html = get_content(self.url, headers={})

        return matchall(html, ['"a-pic-play" href="([^"]+)"'])

site = Hunantv()
