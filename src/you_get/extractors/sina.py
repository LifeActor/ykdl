#!/usr/bin/env python

from ..extractor import VideoExtractor
from ..util import log
from ..util.match import match1
from ..util.html import get_content
from ..common import playlist_not_supported

class Sina(VideoExtractor):
    name = "新浪视频 (sina)"

    def prepare(self, **kwargs):
        assert self.url or self.vid

        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, 'vid:(\w+)', 'ipad_vid:\'(\w+)\'')
            self.title = match1(html, '<title>([^<]+)')
        if not self.vid:
            log.wtf("can't get vid")

        url = 'http://v.iask.com/v_play_ipad.php?vid={}'.format(self.vid)
        title = ""
        if "title" in kwargs and kwargs["title"]:
            title = kwargs["title"]
        else:
            title = self.name + " VID: " + self.vid
        self.title = self.title or title
        self.stream_types.append('current')
        self.streams['current'] = {'container': 'mp4', 'src': [url], 'size' : 0}

site = Sina()
download = site.download_by_url
download_playlist = playlist_not_supported('sina')
