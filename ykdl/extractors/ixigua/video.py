# -*- coding: utf-8 -*-

from .._common import *
from .. import _byted


class IXiGua(Extractor):
    name = '西瓜视频 (IXiGua)'

    profile_2_id = {
       '1080p': 'BD',
        '720p': 'TD',
        '480p': 'HD',
        '360p': 'SD',
     }

    def prepare(self):
        info = MediaInfo(self.name)

        html = _byted.get_content(self.url)
        data = match1(html, 'window._SSR_HYDRATED_DATA=(.+?)</script>')
        self.logger.debug('data: \n%s', data)
        data = json.loads(data.replace('undefined', 'null'))

        video_info = data['anyVideo']['gidInformation']['packerData']['video']

        info.title = video_info['title']
        info.artist = video_info['user_info']['name']
        info.duration = video_info['video_duration']

        for v in video_info['videoResource']['normal']['video_list'].values():
            video_profile = v['definition']
            stream = self.profile_2_id[video_profile]
            info.streams[stream] = {
                'container': v['vtype'],
                'video_profile': video_profile,
                'src' : [unb64(v['main_url'])],
            }

        return info

site = IXiGua()
