#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content
from ykdl.util.match import match1, matchall
from ykdl.extractor import VideoExtractor
import json
import base64, hashlib, time

class Letvcloud(VideoExtractor):
    name = u"乐视云 (Letvcloud)"

    supported_stream_types = ['yuanhua', 'supper', 'high', 'low']

    def letvcloud_download_by_vu(self):
        #ran = float('0.' + str(random.randint(0, 9999999999999999))) # For ver 2.1
        #str2Hash = 'cfflashformatjsonran{ran}uu{uu}ver2.2vu{vu}bie^#@(%27eib58'.format(vu = vu, uu = uu, ran = ran)  #Magic!/ In ver 2.1
        vu, uu = self.vid
        argumet_dict ={'cf' : 'flash', 'format': 'json', 'ran': str(int(time.time())), 'uu': str(uu),'ver': '2.2', 'vu': str(vu), }
        sign_key = '2f9d6924b33a165a6d8b5d3d42f4f987'  #ALL YOUR BASE ARE BELONG TO US
        str2Hash = ''.join([i + argumet_dict[i] for i in sorted(argumet_dict)]) + sign_key
        sign = hashlib.md5(str2Hash.encode('utf-8')).hexdigest()
        html = get_content('http://api.letvcloud.com/gpc.php?' + '&'.join([i + '=' + argumet_dict[i] for i in argumet_dict]) + '&sign={sign}'.format(sign = sign), charset= 'utf-8')
        info = json.loads(html)
        assert info['code'] == 0, info['message']
        video_name = info['data']['video_info']['video_name']
        if '.' in video_name:
            ext = video_name.split('.')[-1]
            self.title = video_name[0:-len(ext)-1]
        else:
            ext = 'mp4'
            self.title = video_name
        available_stream_type = info['data']['video_info']['media'].keys()
        for stream in self.supported_stream_types:
            if stream in available_stream_type:
                urls = [base64.b64decode(info['data']['video_info']['media'][stream]['play_url']['main_url']).decode("utf-8")]
                self.stream_types.append(stream)
                self.streams[stream] = {'container': ext, 'video_profile': stream, 'src': urls, 'size' : 0}

    def prepare(self):

        if self.url and not self.vid:
            #maybe error!!
            self.vid = (vu, uu) = matchall(self.url, ["vu=([^&]+)","uu=([^&]+)"])
        self.letvcloud_download_by_vu()

site = Letvcloud()
