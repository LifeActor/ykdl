#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.util.match import match1

from urllib.parse import unquote

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
    'application/vnd.rn-realmedia-vbr': 'rmvb',
}

extNames = {
    # video
    'm2ts',  'mts',  'm2t', 'ts',   'mkv',  'avi',  # contain
    'mpeg',  'mpg',  'm1v', 'mpv',  'dat',          # MPEG-1
    'mpeg2', 'mpg2', 'm2v', 'mpv2', 'mp2v', 'vob',  # MPEG-2
    'mpeg4', 'mpg4', 'm4v', 'mp4',  'mp4v',         # H.264/MPEG-4 AVC
    'flv',   'f4v',                   # Flash Video # H.264/MPEG-4 AVC
    '3gpp',  '3gp2', '3gp', '3g2',                  # H.264/MPEG-4 AVC
    'h264',  'x264', '264', 'avc',                  # H.264/MPEG-4 AVC
    'h265',  'x265', '265', 'hevc',                 # H.265/HEVC
    'webm',                                         # WebM
    'ogv',                                          # Ogg Media File
    'rm',  'rmvb',                                  # Real Video
    'mov', 'hdmov', 'qt',                           # QuickTime 
    'asf', 'wmv',   'wm',                           # Windows Media Video
    # audio
    'mpa',  'mp1', 'm1a', 'mp2', 'm2a', 'mp3', 'm4a',
    'weba', 'f4a', 'ra',  'ogg', 'oga', 'wav', 'wma',
    'flac', 'ape', 'mka', 'dts', 'aac', 'ac3', 'opus'
    # picture
    'jpeg', 'jpe', 'jpg', 'jpc', 'jp2', 'j2k',
    'tiff', 'bmp', 'png', 'gif', 'jbg', 'webp',
    *contentTypes.values()
}

class Multimedia(VideoExtractor):
    name = 'Multimedia (多媒体文件)'

    def prepare(self):
        # Get file type
        ext = self.url.split('?')[0].split('.')[-1]
        if ext not in extNames:
            ctype = self.resheader['Content-Type'].lower()
            if ctype.startswith('image/'):
                ext = ctype[6:]
            else:
                ext = contentTypes[ctype]

        # Get title
        title = self.resheader.get('Content-Disposition')
        if title:
            title = match1(title, 'attachment;.+?filename\*=([^;]+)')
            if title:
                encoding, _, title = title.strip('"').split("'")
                unquote(title, encoding=encoding)
            else:
                title = match1(title, 'attachment;.+?filename=([^;]+)')
                if title:
                    title = unquote(title.strip('"'))
        if title is None:
            title = self.url.split('?')[0].split('/')[-1]
        if title.endswith('.' + ext):
            title = title[0 : -len(ext) - 1]

        info = VideoInfo(self.name)  # ignore judge live status
        info.title = title
        info.stream_types = ['default']
        info.streams['default'] = {
            'container': ext,
            'video_profile': 'default',
            'src': [self.url],
            'size': int(self.resheader.get('Content-Length', 0))
        }
        return info

site = Multimedia()
