# -*- coding: utf-8 -*-

from .._common import *


class AcBase(Extractor):

    quality_2_id = {
        2160: '4K',
        1080: 'BD',
         720: 'TD',
         540: 'HD',
         360: 'SD',
         270: 'LD'
    }

    def prepare(self):
        info = MediaInfo(self.name)
        html = get_content(self.url)
        info.title, info.artist, sourceVid, m3u8Info = self.get_page_info(html)

        m3u8Info = json.loads(m3u8Info)['adaptationSet'][0]['representation']
        self.logger.debug('m3u8Info:\n%s', m3u8Info)
        url = random.choice(['url', 'backupUrl'])
        for q in m3u8Info:
            quality = int(match1(q['qualityType'], '(\d+)'))
            stream_type = self.quality_2_id[quality]
            if q['frameRate'] > 30:
                stream_type += '-f' + str(int(q['frameRate'] + 0.1))
            stream_profile = q['qualityLabel']
            urls = q[url]
            if not isinstance(urls, list):
                urls = [urls]
            info.streams[stream_type] = {
                'container': 'm3u8',
                'video_profile': stream_profile,
                'src': urls,
                'size': 0
            }

        return info

    def prepare_list(self):
        return ['https://www.acfun.cn' + p for p in self.get_path_list()]
