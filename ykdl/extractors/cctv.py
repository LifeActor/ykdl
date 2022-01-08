# -*- coding: utf-8 -*-

from ._common import *


class CNTV(Extractor):
    name = '央视网 (CNTV)'

    supported_chapters = [
        ['chapters6',   'BD', '超高清 1080P'],
        ['chapters5',   'TD', '超高清 720P'],
        ['chapters4',   'TD', '超清'],
        ['chapters3',   'HD', '高清'],
        ['chapters2',   'SD', '标清'],
        ['lowChapters', 'LD', '流畅']]

    def prepare(self):
        info = MediaInfo(self.name)
        self.vid = match1(self.url, '(?:guid|videoCenterId)=(\w+)',
                                    '(\w+)/index\.shtml')
        if self.url and not self.vid:
            content = get_content(self.url)
            self.vid = match1(content, 'guid\s*=\s*[\'"]([^\'"]+)',
                                       '"videoCenterId","([^"]+)',
                                       'initMyAray\s*=\s*[\'"]([^\'"]+)')
        assert self.vid, 'cant find vid'

        data = get_response('http://vdn.apps.cntv.cn/api/getHttpVideoInfo.do',
                            params={
                                'pid': self.vid,
                                'tsp': int(time.time()),
                                'vn': 2054,
                                'pcv': 152438790
                            }).json()

        info.title = '{} - {}'.format(data['title'], data['play_channel'])

        video_data = data['video']
        for chapters, stream_type, profile in self.supported_chapters:
            stream_data = video_data.get(chapters)
            if stream_data:
                urls = []
                for v in stream_data:
                   urls.append(v['url'])
                info.streams[stream_type] = {
                    'container': 'mp4',
                    'video_profile': profile,
                    'src': urls, 
                    'size' : 0
                }
        return info

site = CNTV()
