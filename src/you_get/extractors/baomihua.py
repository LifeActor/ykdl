#!/usr/bin/env python

from ..common import *
from ..extractor import VideoExtractor
import json

class Baomihua(VideoExtractor):

    name = "爆米花（Baomihua)"

    stream_types = [
        {'id': 'current', 'container': 'unknown', 'video_profile': 'currently'},
    ]


    def prepare(self, **kwargs):
        assert self.url or self.vid


        if self.url and not self.vid:
            html = get_html(self.url)
            self.vid = r1(r'flvid = (\d+);', html)
            self.title = r1(r'<title>(.*)</title>', html)

        if not self.url:
            self.title = self.vid

        html = ''
        while(True):
            html = get_html('http://play.baomihua.com/getvideourl.aspx?flvid=%s' % self.vid)

            try:
               #do not go json!!
               json.load(html)
               continue
            except:
               break

        host = r1(r'host=([^&]*)', html)
        assert host
        type = r1(r'videofiletype=([^&]*)', html)
        assert type
        id = r1(r'&stream_name=([^&]*)', html)
        assert id
        size = int(r1(r'&videofilesize=([^&]*)', html))

        url = "http://%s/pomoho_video/%s.%s" % (host, id, type)

        self.streams['current'] = {'container': type, 'src': [url], 'size' : size}



site = Baomihua()
download = site.download_by_url
download_playlist = playlist_not_supported('baomihua')
