# -*- coding: utf-8 -*-

from ._common import *


SECRETKEY = '6FE26D855E1AEAE090E243EB1AF73685'

class HuomaoTv(VideoExtractor):
    name = '火猫 (Huomao)'

    stream_2_profile = {
        'BD': '原画',
        'TD': '超清',
        'HD': '高清',
        'SD': '标清'
    }

    def prepare(self):
        info = VideoInfo(self.name, True)
        html = get_content(self.url)
        info.title = match1(html, '<title>([^<]+)').split('_')[0]

        data = json.loads(match1(html, 'channelOneInfo = ({.+?});'))
        tag_from = 'huomaoh5room'
        tn = str(int(time.time()))
        sign_context = data['stream'] + tag_from + tn + SECRETKEY

        stream_data = get_response('https://www.huomao.com/swf/live_data',
                                   data={
                                       'streamtype': 'live',
                                       'VideoIDS': data['stream'],
                                       'time': tn,
                                       'cdns' : 1,
                                       'from': tag_from,
                                       'token': hash.md5(sign_context)
                                   }).json()
        assert stream_data['roomStatus'] == '1', 'The live stream is offline!'
        for stream in stream_data['streamList']:
            if stream['default'] == 1:
                defstream = stream['list']

        for stream in defstream:
            info.stream_types.append(stream['type'])
            info.streams[stream['type']] = {
                'container': 'flv',
                'video_profile': self.stream_2_profile[stream['type']],
                'src' : [stream['url']],
                'size': float('inf')
            }

        return info

site = HuomaoTv()
