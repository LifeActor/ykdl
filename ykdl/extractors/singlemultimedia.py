# -*- coding: utf-8 -*-

from ._common import *


# TODO: add more supported types and move to ykdl.util
# REF: https://www.iana.org/assignments/media-types/media-types.xhtml

contentTypes = {
    'audio/basic': 'au',
    'audio/mpeg': 'mp3',
    'audio/x-aiff': 'aif',
    'audio/x-pn-realaudio': 'ra',
    'audio/x-wav': 'wav',
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
    # HLS
    'm3u',
    *contentTypes.values()
}

class Multimedia(Extractor):
    name = 'Multimedia (多媒体文件)'

    def prepare(self):
        # Get file type
        ext = self.url.split('?')[0].split('.')[-1]
        if ext not in extNames:
            ctype = self.resinfo['Content-Type'].lower()
            if ctype.startswith('image/'):
                ext = ctype[6:]
            else:
                ext = contentTypes[ctype]

        # Get title
        title = self.resinfo.get_filename()
        if title is None:
            title = self.url.split('?')[0].split('/')[-1]
        if title.endswith('.' + ext):
            title = title[0 : -len(ext) - 1]

        info = MediaInfo(self.name)
        info.title = title
        if ext[:3] == 'm3u':
            info.streams = load_m3u8_playlist(self.url)
        else:
            info.streams['current'] = {
                'container': ext,
                'profile': 'current',
                'src': [self.url],
                'size': int(self.resinfo.get('Content-Length', 0))
            }
        return info

site = Multimedia()
