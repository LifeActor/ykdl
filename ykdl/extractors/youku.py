#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content, add_header
from ykdl.util.match import match1, matchall
from ykdl.util import log
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo

import time
import json

supported_stream_code = [ 'mp4hd3', 'hd3', 'mp4hd2', 'hd2', 'mp4hd', 'mp4', 'flvhd', 'flv', '3gphd' ]
ids = ['BD', 'TD', 'HD', 'SD', 'LD']
stream_code_to_id = {
    'mp5hd3': 'BD',
    'mp4hd3': 'BD',
    'hd3'   : 'BD',
    'mp5hd2': 'TD',
    'mp4hd2': 'TD',
    'hd2'   : 'TD',
    'mp5hd' : 'HD',
    'mp4hd' : 'HD',
    'mp4'   : 'HD',
    'flvhd' : 'SD',
    'flv'   : 'SD',
    '3gphd' : 'LD'
}
stream_code_to_profiles = {
    'BD' : u'1080p',
    'TD' : u'超清',
    'HD' : u'高清',
    'SD' : u'标清',
    'LD' : u'标清（3GP）'
}
id_to_container = {
    'BD' : 'flv',
    'TD' : 'flv',
    'HD' : 'mp4',
    'SD' : 'flv',
    'LD' : 'mp4'
}

class Youku(VideoExtractor):
    name = u"优酷 (Youku)"


    def prepare(self):
        info = VideoInfo(self.name)        

        if self.url and not self.vid:
             self.vid = match1(self.url, 'youku\.com/v_show/id_([a-zA-Z0-9=]+)' ,\
                                         'player\.youku\.com/player\.php/sid/([a-zA-Z0-9=]+)/v\.swf',\
                                         'loader\.swf\?VideoIDS=([a-zA-Z0-9=]+)',\
                                         'loader\.swf\?VideoIDS=([a-zA-Z0-9=]+)',\
                                         'player\.youku\.com/embed/([a-zA-Z0-9=]+)')

        api_url = 'https://ups.youku.com/ups/get.json?vid={}&ccode=0401&client_ip=192.168.1.1&utid=&client_ts={}'.format(self.vid, int(time.time()))

        data = json.loads(get_content(api_url))
        assert data['e']['code'] == 0, data['e']['desc']
        data = data['data']
        info.title = data['video']['title']
        streams = data['stream']
        for s in streams:
            t = stream_code_to_id[s['stream_type']]
            urls = [ json.loads(get_content(u['cdn_url']+'&yxon=1&special=true'))[0]['server']  for   u in s['segs']]
            size = s['size']
            info.stream_types.append(t)
            info.streams[t] =  {
                    'container': id_to_container[t],
                    'video_profile': stream_code_to_profiles[t],
                    'size': size,
                    'src' : urls
                }
        info.stream_types = sorted(info.stream_types, key = ids.index)
        return info


site = Youku()
