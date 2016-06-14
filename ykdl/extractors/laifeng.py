#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1
from ykdl.extractor import VideoExtractor

import json
from random import randint

class Laifeng(VideoExtractor):
    name = u'laifeng (来疯直播)'

    def prepare(self):
        assert self.url, "please provide valid url"
        self.live = True
        html = get_content(self.url)
        Alias = match1(html, 'initAlias:\'([^\']+)')
        Token = match1(html, 'initToken: \'([^\']+)')
        self.artist = match1(html, 'anchorName:\'([^\']+)')
        self.title = self.artist + u'的直播房间'

        api_url = "http://lapi.xiu.youku.com/v1/get_playlist?app_id=101&alias={}&token={}&player_type=flash&sdkversion=0.1.0&playerversion=3.1.0&rd={}".format(Alias, Token, randint(0,9999))
        data1 = json.loads(get_content(api_url))

        assert data1['error_code'] == 0

        url_data = data1['url_list'][0]

        stream_url = json.loads(get_content(url_data['url']))['u']

        self.stream_types.append('current')
        self.streams['current'] = {'container': url_data["format"], 'video_profile': 'current', 'src' : [stream_url], 'size': float('inf')}

site = Laifeng()
