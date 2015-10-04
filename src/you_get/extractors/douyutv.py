#!/usr/bin/env python

from ..common import *
from ..extractor import VideoExtractor
import hashlib
import time

class Douyutv(VideoExtractor):
    name = '斗鱼 (DouyuTV)'

    def prepare(self, **kwargs):
        assert self.url or self.vid

        if self.url:
            self.vid = self.url[self.url.rfind('/')+1:]

        suffix = 'room/%s?aid=android&client_sys=android&time=%d' % (self.vid, int(time.time()))
        sign = hashlib.md5((suffix + '1231').encode('ascii')).hexdigest()
        json_request_url = "http://www.douyutv.com/api/v1/%s&auth=%s" % (suffix, sign)
        content = get_content(json_request_url)
        data = json.loads(content)['data']
        server_status = data.get('error',0)
        if server_status is not 0:
            raise ValueError("Server returned error:%s" % server_status)
        self.title = data.get('room_name')
        show_status = data.get('show_status')
        if show_status is not "1":
            raise ValueError("The live stream is not online! (Errno:%s)" % show_status)
        real_url = data.get('rtmp_url')+'/'+data.get('rtmp_live')
        self.stream_types.append('current')
        self.streams['current'] = {'container': 'flv', 'video_profile': 'current', 'src' : [real_url], 'size': float('inf')}

    def download_playlist(self, url, **kwargs):
        self.url = url
        html = get_content(self.url)
        vids = matchall(html, ['class="hroom_id" value="([^"]+)'])

        for vid in vids:
            self.download_by_vid(vid, **kwargs)

site = Douyutv()
download = site.download_by_url
download_playlist = site.download_playlist
