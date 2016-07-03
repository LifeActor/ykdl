#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.extractor import VideoExtractor
from ykdl.util.html import get_content, add_header
from ykdl.util.match import match1
from ykdl.videoinfo import VideoInfo

import json
from xml.dom.minidom import parseString

class TDorig(VideoExtractor):
    name = u"土豆原创 (tudou)"

    def prepare(self):
        info = VideoInfo(self.name)
        info.title = self.name + ' ' + str(self.vid)
        add_header('User-Agent', '')

        data = json.loads(get_content('http://www.tudou.com/outplay/goto/getItemSegs.action?iid=%s' % self.vid))

        temp = max([data[i] for i in data if 'size' in data[i][0]], key=lambda x:sum([part['size'] for part in x]))
        vids, size = [t["k"] for t in temp], sum([t["size"] for t in temp])

        urls = []
        for vid in vids:
            for i in parseString(get_content('http://ct.v2.tudou.com/f?id=%s' % vid)).getElementsByTagName('f'):
                urls.append(i.firstChild.nodeValue.strip())

        ext = match1(urls[0], 'http://[\w.]*/(\w+)/[\w.]*')
        info.stream_types.append('current')
        info.streams['current'] = {'container': ext, 'video_profile': 'current', 'src' : urls, 'size': size}
        return info

site = TDorig()
