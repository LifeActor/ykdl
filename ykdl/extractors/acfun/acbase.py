#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content, add_header
from ykdl.util.match import match1, matchall
from ykdl.embedextractor import EmbedExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.compact import urljoin

import json

class AcBase(EmbedExtractor):

    stream_ids = ['BD', 'TD', 'HD', 'SD', 'LD']
    quality_2_id = {
        1080: 'BD',
        720: 'TD',
        540: 'HD',
        360: 'SD',
        270: 'LD'
    }
    id_2_profile = {
        'BD': u'1080P',
        'TD': u'超清',
        'HD': u'高清',
        'SD': u'标清',
        'LD': u'流畅'
    }

    def check_uptime(self, uptime):
        # fallback to m3u8 (zhuzhan)
        # 1565827200000 == 2019-08-15 00:00:00
        self.parse_m3u8 = uptime > 1565827200000

    def prepare(self):
        self.parse_m3u8 = False
        html = get_content(self.url)
        title, artist, sourceVid, m3u8Info = self.get_page_info(html)

        add_header('Referer', 'https://www.acfun.cn/')
        if not self.parse_m3u8:
            try:
                data = json.loads(get_content('https://www.acfun.cn/video/getVideo.aspx?id={}'.format(sourceVid)))

                sourceType = data['sourceType']
                sourceId = data['sourceId']
                if sourceType == 'zhuzhan':
                    sourceType = 'acfun.zhuzhan'
                    encode = data['encode']
                    sourceId = (sourceId, encode)
                elif sourceType == 'letv':
                    # workaround for letv, because it is letvcloud
                    sourceType = 'le.letvcloud'
                    sourceId = (sourceId, '2d8c027396')
                elif sourceType == 'qq':
                    sourceType = 'qq.video'

                self.video_info = {
                    'site': sourceType,
                    'vid': sourceId,
                    'title': title,
                    'artist': artist
                }

            except IOError:
                self.parse_m3u8 = True

        if self.parse_m3u8:
            info = VideoInfo(self.name)
            info.title = title
            info.artist = artist

            if m3u8Info is None:
                data = json.loads(get_content('https://www.acfun.cn/rest/pc-direct/play/playInfo/m3u8Auto?videoId={}'.format(sourceVid)))
                m3u8Info = data['playInfo']['streams'][0]
            # some videos are broken with CDN, choose them here
            m3u8api = m3u8Info['playUrls'][-1]
            lines = get_content(m3u8api)
            self.logger.debug('m3u8 api: %s', lines)
            lines = lines.split('\n')

            resolution = None
            for line in lines:
                if resolution is None:
                    resolution = match1(line, 'RESOLUTION=(\d+x\d+)')
                elif match1(line, '(\.m3u8)'):
                    quality = min(int(q) for q in resolution.split('x'))
                    resolution = None
                    if line.startswith('http'):
                        url = line
                    else:
                        url = urljoin(m3u8api, line)
                    stream_type = self.quality_2_id[quality]
                    stream_profile = self.id_2_profile[stream_type]
                    info.stream_types.append(stream_type)
                    info.streams[stream_type] = {
                        'container': 'm3u8',
                        'video_profile': stream_profile,
                        'src': [url],
                        'size': 0
                    }

            info.stream_types = sorted(info.stream_types, key=self.stream_ids.index)
            self.video_info['info'] = info

    def prepare_playlist(self):
        for p in self.get_path_list():
            next_url = 'https://www.acfun.cn' + p
            video_info = self.new_video_info()
            video_info['url'] = next_url
            self.video_info_list.append(video_info)
