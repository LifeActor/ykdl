#!/usr/bin/env python
import json

from ..util.match import match1
from ..util.html import get_content
from ..extractor import VideoExtractor


class Baomihua(VideoExtractor):

    name = "爆米花（Baomihua)"

    def prepare(self):
        assert self.url or self.vid


        if self.url and not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, r'flvid = (\d+);')
            self.title = match1(html, '<title>(.*)</title>')

        if not self.url:
            self.title = self.name + str(self.vid)

        html = ''
        while(True):
            html = get_content('http://play.baomihua.com/getvideourl.aspx?flvid=%s' % self.vid)

            try:
               #do not go json!!
               json.load(html)
               continue
            except:
               break

        host = match1(html, 'host=([^&]*)')
        assert host
        type = match1(html, 'videofiletype=([^&]*)')
        assert type
        id = match1(html, '&stream_name=([^&]*)')
        assert id
        size = int(match1(html, '&videofilesize=([^&]*)'))

        url = "http://%s/pomoho_video/%s.%s" % (host, id, type)
        self.stream_types.append('current')
        self.streams['current'] = {'container': type, 'src': [url], 'size' : size}

site = Baomihua()
