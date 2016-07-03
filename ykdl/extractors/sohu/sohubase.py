#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.compact import urlparse

import json
import time
from random import random

'''
Changelog:
    1. http://tv.sohu.com/upload/swf/20150604/Main.swf
        new api
'''


class SohuBase(VideoExtractor):

    supported_stream_types = [ 'oriVid', 'superVid', 'highVid', 'norVid' ]
    types_2_id = { 'oriVid': 'BD', 'superVid': 'TD', 'highVid': 'HD', 'norVid': 'SD' }
    types_2_profile = { 'oriVid': u'原画', 'superVid': u'超清', 'highVid': u'高清', 'norVid': u'标清' }
    realurls = { 'BD': [], 'TD': [], 'HD': [], 'SD': []}

    def parser_info(self, video, info, stream, lvid):
        if not 'allot' in info:
            return
        stream_id = self.types_2_id[stream]
        stream_profile = self.types_2_profile[stream]
        host = info['allot']
        prot = info['prot']
        tvid = info['tvid']
        data = info['data']
        size = sum(map(int,data['clipsBytes']))
        assert len(data['clipsURL']) == len(data['clipsBytes']) == len(data['su'])
        for new, clip, ck, in zip(data['su'], data['clipsURL'], data['ck']):
            clipURL = urlparse(clip).path
            self.realurls[stream_id].append('http://'+host+'/?prot=9&prod=flash&pt=1&file='+clipURL+'&new='+new +'&key='+ ck+'&vid='+str(self.vid)+'&uid='+str(int(time.time()*1000))+'&t='+str(random())+'&rb=1')
        video.streams[stream_id] = {'container': 'mp4', 'video_profile': stream_profile, 'size' : size}
        video.stream_types.append(stream_id)
        self.extract_single(video, stream_id)

    def prepare(self):
        video = VideoInfo(self.name)
        if self.url and not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, '\/([0-9]+)\/v\.swf', '\&id=(\d+)')

        info = json.loads(get_content(self.apiurl % self.vid))
        if info['status'] == 1:
            data = info['data']
            video.title = data['tvName']
            for stream in self.supported_stream_types:
                lvid = data[stream]
                if lvid == 0 or not lvid:
                    continue
                if lvid != self.vid :
                    info = json.loads(get_content(self.apiurl % lvid))

                self.parser_info(video, info, stream, lvid)
        return video


    def extract_single(self, video, stream_id):
        urls = []
        for url in self.realurls[stream_id]:
            info = json.loads(get_content(url))
            urls.append(info['url'])
        video.streams[stream_id]['src'] = urls
