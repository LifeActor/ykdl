#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from ..util.match import match1
from ..util.html import get_content, add_header
from ..extractor import VideoExtractor
from ykdl.compact import compact_unquote


class Baomihua(VideoExtractor):

    name = u"爆米花（Baomihua)"

    def prepare(self):


        if self.url:
            self.vid = match1(self.url, '_(\d+)', 'm/(\d+)')

        add_header('Referer', 'http://m.video.baomihua.com/')
        html = get_content('http://play.baomihua.com/getvideourl.aspx?flvid={}&datatype=json&devicetype=wap'.format(self.vid))
        data = json.loads(html)
        self.title = compact_unquote(data["title"])
        host = data['host']
        stream_name = data['stream_name']
        t = data['videofiletype']
        size = int(data['videofilesize'])

        url = "http://{}/pomoho_video/{}.{}".format(host, stream_name, t)
        self.stream_types.append('current')
        self.streams['current'] = {'video_profile': 'current', 'container': t, 'src': [url], 'size' : size}

site = Baomihua()
