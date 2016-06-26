#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..extractor import VideoExtractor
from xml.dom.minidom import parseString
from ..util.html import get_content
from ..util.match import match1

class Ifeng(VideoExtractor):
    name = u'凤凰视频 (ifeng)'

    supported_stream_types = ['500k', '350k']
    types_2_id = {'500k': 'HD', '350k':'SD'}
    types_2_profile = {'500k': u'高清', '350k':u'标清'}
    ids = ['HD', 'SD']
    def prepare(self):

        if not self.vid:
            self.vid= match1(self.url, '#([a-zA-Z0-9\-]+)', '/([a-zA-Z0-9\-]+).shtml')

        xml = get_content('http://v.ifeng.com/video_info_new/{}/{}/{}.xml'.format(self.vid[-2], self.vid[-2:], self.vid))
        doc = parseString(xml.encode('utf-8'))
        self.title = doc.getElementsByTagName('item')[0].getAttribute("Name")
        videos = doc.getElementsByTagName('videos')
        for v in videos[0].getElementsByTagName('video'):
            if v.getAttribute("mediaType") == 'mp4':
                _t = v.getAttribute("type")
                _u = v.getAttribute("VideoPlayUrl")
                stream_id = self.types_2_id[_t]
                stream_profile = self.types_2_profile[_t]
                self.stream_types.append(stream_id)
                self.streams[stream_id] = {'container': 'mp4', 'video_profile': stream_profile, 'src' : [_u], 'size': 0}

        self.stream_types = sorted(self.stream_types, key = self.ids.index)

site = Ifeng()
