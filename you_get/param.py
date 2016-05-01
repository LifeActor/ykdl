#!/usr/bin/env python
import getopt
import sys
from .util import log

version = 'You-Get, a video downloader.'
help = 'Usage: You-Get [OPTION]... [URL]...\n'
help += '''\nStartup options:
-V | --version                           Display the version and exit.
-h | --help                              Print this help and exit.
'''
help += '''\nDownload options (use with URLs):
-f | --force                             Force overwriting existed files.
-i | --info                              Display the information of videos without downloading.
-u | --url                               Display the real URLs of videos without downloading.
-c | --cookies                           Load NetScape's cookies.txt file.
-F | --format <STREAM_ID>                Video format code.
-o | --output-dir <PATH>                 Set the output directory for downloaded videos.
-p | --player <PLAYER [options]>         Directly play the video with PLAYER like vlc/smplayer.
-x | --http-proxy <HOST:PORT>            Use specific HTTP proxy for downloading.
-y | --extractor-proxy <HOST:PORT>       Use specific HTTP proxy for extracting stream data.
     --no-proxy                          Don't use any proxy. (ignore $http_proxy)
     --debug                             Show traceback on KeyboardInterrupt.
'''

class Param():

    short_opts = 'lVhfiujF:o:p:'
    opts = ['playlist', 'version', 'help', 'force', 'info', 'url', 'format=', 'output-dir=', 'player=', 'json']

    def __init__(self, param_string):
        self.dry_run = False
        self.force = False
        self.player = None
        self.stream_id = None
        self.info_only = False
        self.playlist = False
        self.lang = None
        self.output_dir = '.'
        self.urls = None
        self.json_out = False

        try:
            opts, self.urls = getopt.getopt(param_string, self.short_opts, self.opts)
        except getopt.GetoptError as err:
            log.e(err)
            log.e("try 'you-get --help' for more options")
            sys.exit(2)
        for o, a in opts:
            if o in ('-V', '--version'):
                print(version)
                sys.exit()
            elif o in ('-h', '--help'):
                print(version)
                print(help)
                sys.exit()
            elif o in ('-f', '--force'):
                self.force = True
            elif o in ('-i', '--info'):
                self.info_only = True
            elif o in ('-u', '--url'):
                self.dry_run = True
            elif o in ('-l', '--playlist'):
                self.playlist = True
            elif o in ('-F', '--format'):
                self.stream_id = a
            elif o in ('-o', '--output-dir'):
                self.output_dir = a
            elif o in ('-p', '--player'):
                self.player = a
            elif o in ('--lang',):
                self.lang = a
            elif o in ('--json', '-j'):
                self.json_out = True
            else:
                log.e("try 'you-get --help' for more options")
                sys.exit(2)
        if not self.urls:
            print(help)
            sys.exit()
