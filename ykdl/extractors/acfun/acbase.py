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

        self.mid  # scan & check
        html = get_content(self.url)
        info.title, info.artist, sourceVid, data = self.get_page_info(html)

        data = json.loads(data)['adaptationSet'][0]['representation']
        self.logger.debug('data:\n%s', data)

        url = random.choice(['url', 'backupUrl'])
        for q in data:
            quality = int(match1(q['qualityType'], '(\d+)'))
            stream_id = self.quality_2_id[quality]
            if q['frameRate'] > 30:
                stream_id += '-f' + str(int(q['frameRate'] + 0.1))
            stream_profile = q['qualityLabel']
            urls = q[url]
            if not isinstance(urls, list):
                urls = [urls]
            info.streams[stream_id] = {
                'container': 'm3u8',
                'profile': stream_profile,
                'src': urls
            }

        return info
