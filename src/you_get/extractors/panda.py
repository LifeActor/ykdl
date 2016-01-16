#!/usr/bin/env python
from ..common import playlist_not_supported
from ..extractor import VideoExtractor
from ..util.html import get_content
from ..util.match import match1
import json

class Panda(VideoExtractor):
    name = '熊猫TV (Panda)'

    live_base = "http://pl3.live.panda.tv/live_panda/{}.flv"
    api_url = "http://www.panda.tv/api_room?roomid={}"

    def prepare(self, **kwargs):
        assert self.url or self.vid

        if not self.vid:
            self.vid = match1(self.url, 'panda.tv/(\w+)')

        content = get_content(self.api_url.format(self.vid))
        stream_data = json.loads(content)
        if stream_data["errno"] == 0:
            room_key = stream_data['data']['videoinfo']['room_key']
            self.title = stream_data['data']['roominfo']['name']
        else:
           from ..util import log
           log.e("error: {}, {}".format(stream_data["errno"], stream_data["errmsg"]))
           exit(1)

        self.stream_types.append('current')
        self.streams['current'] = {'container': 'flv', 'video_profile': 'current', 'src' : [self.live_base.format(room_key)], 'size': float('inf')}

site = Panda()
download = site.download_by_url
download_playlist = playlist_not_supported('Panda')
