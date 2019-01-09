#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.util.html import get_location_and_header
from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo

import json

contentTypes = {
    'video/3gpp': '3gp',
    'video/3gpp2': '3p2',
    'video/avi': 'avi',
    'video/mp2t': 'ts',
    'video/mp4': 'mp4',
    'video/mpeg': 'mp2v',
    'video/mpeg4': 'mp4',
    'video/mpg': 'mpg',
    'video/ogg': 'ogg',
    'video/quicktime': 'mov',
    'video/vnd.mpegurl': 'mxu',
    'video/vnd.ms-playready.media.pyv': 'pyv',
    'video/vnd.rn-realvideo': 'rv',
    'video/vnd.uvvu.mp4': 'uvu',
    'video/vnd.vivo': 'viv',
    'video/webm': 'webm',
    'video/x-f4v': 'f4v',
    'video/x-fli': 'fli',
    'video/x-flv': 'flv',
    'video/x-ivf': 'IVF',
    'video/x-sgi-movie': 'movie',
    'video/x-m4v': 'm4v',
    'video/x-mpeg': 'mpe',
    'video/x-mpg': 'mpa',
    'video/x-msvideo': 'avi',
    'video/x-ms-asf': 'asf',
    'video/x-ms-wm': 'wm',
    'video/x-ms-wmv': 'wmv',
    'video/x-ms-wmx': 'wmx',
    'video/x-ms-wvx': 'wvx',
    'application/x-mpegurl': 'm3u8',
    'application/vnd.apple.mpegurl': 'm3u8',
    'application/vnd.rn-realmedia': 'rm',
    'application/vnd.rn-realmedia-secure': 'rms',
    'application/vnd.rn-realmedia-vbr': 'rmvb'
}

extNames = contentTypes.values()

class VideoFile(VideoExtractor):
    name = u'Download directly'

    def prepare(self):
        # Get file type
        ext = self.url.split('?')[0].split('.')[-1]
        if not ext in extNames:
            location, header = get_location_and_header(self.url)
            type = header['Content-Type'].lower()
            ext = contentTypes[type]
        
        # Get title
        title = self.url.split('?')[0].split('/')[-1]
        if title.endswith('.' + ext):
            title = title.split('.')[0:-1]
        
        info = VideoInfo(self.name)
        info.title = title
        info.stream_types = 'default'
        info.streams['default'] = {
            'container': ext,
            'video_profile': 'default',
            'src': [self.url],
            'size': 0
        }
        return info

site = VideoFile()
