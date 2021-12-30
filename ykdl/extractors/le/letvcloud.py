# -*- coding: utf-8 -*-

from .._common import *


class Letvcloud(Extractor):
    name = '乐视云 (Letvcloud)'

    stream_2_id_profile = {
        'yuanhua': ['BD', '原画'],
          'super': ['TD', '超清'],
           'high': ['HD', '高清'],
            'low': ['SD', '标清']
    }

    def letvcloud_download_by_vu(self):
        info = MediaInfo(self.name)
        #ran = float('0.' + str(random.randint(0, 9999999999999999))) # For ver 2.1
        #str2Hash = 'cfflashformatjsonran{ran}uu{uu}ver2.2vu{vu}bie^#@(%27eib58'.format(vu = vu, uu = uu, ran = ran)  #Magic!/ In ver 2.1
        vu, uu = self.vid
        params ={
            'cf' : 'flash',
            'format': 'json',
            'ran': int(time.time()),
            'uu': uu,
            'ver': '2.2',
            'vu': vu
        }
        sign_key = '2f9d6924b33a165a6d8b5d3d42f4f987'  #ALL YOUR BASE ARE BELONG TO US
        str2Hash = ''.join([i + str(params[i]) for i in sorted(params)])
        params['sign'] = hash.md5(str2Hash + sign_key)
        data = get_response('http://api.letvcloud.com/gpc.php',
                            params=params).json()
        assert data['code'] == 0, data['message']
        data = data['data']['video_info']

        video_name = data['video_name']
        if '.' in video_name:
            ext = video_name.split('.')[-1]
            info.title = video_name[0:-len(ext)-1]
        else:
            ext = 'mp4'
            info.title = video_name

        media = data['media']
        for st, (stream, profile) in self.stream_2_id_profile.items():
            if st not in media:
                continue
            url = base64.b64decode(media[st]['play_url']['main_url']).decode()
            info.streams[stream] = {
                'container': ext,
                'video_profile': profile,
                'src': [url],
                'size' : 0
            }
        return info

    def prepare(self):

        if self.url and not self.vid:
            #maybe error!!
            self.vid = (vu, uu) = matchall(self.url, 'vu=([^&]+)','uu=([^&]+)')
        return self.letvcloud_download_by_vu()

site = Letvcloud()
