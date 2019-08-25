#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_content, add_header
from ykdl.util.match import match1, matchall
from ykdl.embedextractor import EmbedExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.compact import urljoin

import json

class AcBase(EmbedExtractor):

    stream_ids = ['BD', 'TD', 'HD', 'SD']
    quality_2_id = {
        '1920': 'BD',
        '1280': 'TD',
        '960':  'HD',
        '640':  'SD'
    }
    id_2_profile = {
        'BD': u'1080P',
        'TD': u'超清',
        'HD': u'高清',
        'SD': u'标清'
    }

    def check_uptime(self, uptime):
        uptime = ''.join(['{:0>2}'.format(i) for i in uptime.split('-')])
        return uptime > '20190814'

    def prepare(self):
        html = get_content(self.url)
        title, artist, sourceVid, m3u8Info = self.get_page_info(html)

        add_header('Referer', 'https://www.acfun.cn/')
        try:
            if sourceVid is None:
                # fallback to m3u8 (zhuzhan)
                raise IOError

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
            info = VideoInfo(self.name)
            info.title = title
            info.artist = artist

            if m3u8Info is None:
                data = json.loads(get_content('https://www.acfun.cn/rest/pc-direct/play/playInfo/m3u8Auto?videoId={}'.format(sourceVid)))
                m3u8Info = data['playInfo']['streams'][0]
            m3u8api = m3u8Info['playUrls'][0]
            lines = get_content(m3u8api)
            self.logger.debug('m3u8 api: %s', lines)
            lines = lines.split('\n')

            resolution = None
            for line in lines:
                if resolution is None:
                    resolution = match1(line, 'RESOLUTION=(\d+x\d+)')
                elif match1(line, '(\.m3u8)'):
                    quality = resolution.split('x')[0]
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
