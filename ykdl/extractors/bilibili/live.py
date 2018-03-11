#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.util.html import get_content, get_location
from ykdl.util.match import match1, matchall

import json

class BiliLive(VideoExtractor):
    name = u"Bilibili live (哔哩哔哩 直播)"

    supported_stream_profile = [u'原画', u'超清', u'高清', u'流畅']
    profile_2_type = {u'原画': 'BD', u'超清': 'TD', u'高清': 'HD', u'流畅' :'SD'}

    def prepare(self):
        info = VideoInfo(self.name, True)
        ID = match1(self.url, "/(\d+)")
        api1_data = json.loads(get_content("https://api.live.bilibili.com/room/v1/Room/room_init?id={}".format(ID)))
        self.vid = api1_data["data"]["room_id"]
        api2_data = json.loads(get_content("https://api.live.bilibili.com/room/v1/Room/get_info?room_id={}&from=room".format(self.vid)))
        info.title = api2_data["data"]["title"]
        assert api2_data["data"]["live_status"] == 1, u"主播正在觅食......"
        for profile in self.supported_stream_profile:
            data = json.loads(get_content("https://api.live.bilibili.com/api/playurl?player=1&cid={}&quality={}&platform=flash&otype=json".format(self.vid, 4-self.supported_stream_profile.index(profile))))
            urls = [data["durl"][0]["url"]]
            size = float('inf')
            ext = 'flv'
            info.stream_types.append(self.profile_2_type[profile])
            info.streams[self.profile_2_type[profile]] = {'container': ext, 'video_profile': profile, 'src' : urls, 'size': size}
        return info

site = BiliLive()
