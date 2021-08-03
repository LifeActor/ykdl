#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content, add_header
from ykdl.util.match import match1, matchall
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.compact import urljoin

import json
import random

class AcBase(VideoExtractor):

    stream_ids = ['4K', 'BD', 'TD', 'HD', 'SD', 'LD']
    quality1_2_id = {
        # min resolution
        2160: '4K',
        1080: 'BD',
        720: 'TD',
        540: 'HD',
        360: 'SD',
        270: 'LD'
    }
    quality2_2_id = {
        # max resolution
        3840: '4K',
        1920: 'BD',
        1280: 'TD',
        960: 'HD',
        640: 'SD',
        480: 'LD'
    }
    id_2_profile = {
        '4K': u'2160P',
        'BD': u'1080P',
        'TD': u'720P',
        'HD': u'540P',
        'SD': u'360P',
        'LD': u'270P'
    }

    def prepare(self):
        info = VideoInfo(self.name)
        html = get_content(self.url)
        info.title, info.artist, sourceVid, m3u8Info = self.get_page_info(html)

        if isinstance(m3u8Info, str):
            m3u8Info = json.loads(m3u8Info)['adaptationSet'][0]['representation']
            url = random.choice(['url', 'backupUrl'])
            for q in m3u8Info:
                quality = int(match1(q['qualityType'], '(\d+)'))
                stream_type = self.quality1_2_id[quality]
                stream_profile = q['qualityLabel']
                urls = q[url]
                if not isinstance(urls, list):
                    urls = [urls]
                if stream_type not in info.streams:
                    info.stream_types.append(stream_type)
                elif stream_profile.endswith('P60'):
                    # drop 60 FPS
                    continue
                info.streams[stream_type] = {
                    'container': 'm3u8',
                    'video_profile': stream_profile,
                    'src': urls,
                    'size': 0
                }

        else:
            add_header('Referer', 'https://www.acfun.cn/')

            if m3u8Info is None:
                data = json.loads(get_content('https://www.acfun.cn/rest/pc-direct/play/playInfo/m3u8Auto?videoId={}'.format(sourceVid)))
                m3u8Info = data['playInfo']['streams'][0]

            # some videos are broken of CDN, random choose one
            m3u8api = random.choice(m3u8Info['playUrls'])
            self.logger.warning('Request m3u8 info via CDN: %s\nIf video has broken on this CDN, please retry.', m3u8api)
            lines = get_content(m3u8api)
            self.logger.debug('m3u8 api: %s', lines)
            lines = lines.split('\n')

            resolutions = None
            for line in lines:
                if resolutions is None:
                    resolutions = match1(line, 'RESOLUTION=(\d+x\d+)')
                    if resolutions:
                        resolutions = [int(q) for q in resolutions.split('x')]
                elif match1(line, '(\.m3u8)'):
                    try:
                        quality = min(resolutions)
                        stream_type = self.quality1_2_id[quality]
                    except:
                        quality = max(resolutions)
                        stream_type = self.quality2_2_id[quality]
                    resolutions = None
                    if line.startswith('http'):
                        url = line
                    else:
                        url = urljoin(m3u8api, line)
                    stream_profile = self.id_2_profile[stream_type]
                    if stream_type not in info.streams:
                        info.stream_types.append(stream_type)
                    info.streams[stream_type] = {
                        'container': 'm3u8',
                        'video_profile': stream_profile,
                        'src': [url],
                        'size': 0
                    }

        info.stream_types = sorted(info.stream_types, key=self.stream_ids.index)
        return info

    def prepare_list(self):
        return ['https://www.acfun.cn' + p for p in self.get_path_list()]
