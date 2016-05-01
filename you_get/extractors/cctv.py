#!/usr/bin/env python

from ..util.html import get_content
from ..util.match import match1
from ..extractor import VideoExtractor
from ..util import log

import json

class CNTV(VideoExtractor):
    name = '央视网 (cntv)'

    supported_stream_types = ['normal', 'low']
    type_2_cpt = { 'normal':'chapters', 'low':'lowChapters' }

    def prepare(self):
        assert self.url or self.vid

        if self.url and not self.vid:
            content = get_content(self.url)
            self.vid = match1(content, 'videoId:"([^"]+)', '_guid="([^"]+)')
        if not self.vid:
            log.wtf('cant find vid')

        html = get_content('http://vdn.apps.cntv.cn/api/getIpadVideoInfo.do?pid={}&tai=ipad&from=html5'.format(self.vid))
        data = json.loads(match1(html, '\'([^\']+)'))
        video_data = data['video']
        self.title = data['title']

        for t in self.supported_stream_types:
            if self.type_2_cpt[t] in video_data:
                urls = []
                for v in video_data[self.type_2_cpt[t]]:
                   urls.append(v['url'])
                self.stream_types.append(t)
                self.streams[t] = {'container': 'mp4', 'video_profile': t, 'src': urls, 'size' : 0}

site = CNTV()
