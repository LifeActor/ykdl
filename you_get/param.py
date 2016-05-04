#!/usr/bin/env python
import getopt
import sys
from .util import log

version = 'You-Get, a video downloader. Forked form you-get 0.3.34@soimort'
help = 'Usage: You-Get [OPTION]... [URL]...\n'
help += '''\nStartup options:
-V | --version                           Display the version and exit.
-h | --help                              Print this help and exit.
'''
help += '''\nDownload options (use with URLs):
-i | --info                              Display the information of videos without downloading.
-u | --url                               Display the real URLs of videos without downloading.
-j | --json                              Display info in json format
-F | --format <STREAM_ID>                Video format code.
-o | --output-dir <PATH>                 Set the output directory for downloaded videos.
-p | --player <PLAYER [options]>         Directly play the video with PLAYER like vlc/smplayer.
-l | --playlist                          Download as a playlist
'''

class Param():

    short_opts = 'lVhiujF:o:p:'
    opts = ['playlist', 'version', 'help', 'info', 'url', 'format=', 'output-dir=', 'player=', 'json']

    def __init__(self, param_string):
        self.dry_run = False
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
            elif o in ('--json', '-j'):
                self.json_out = True
            else:
                log.e("try 'you-get --help' for more options")
                sys.exit(2)
        if not self.urls:
            print(help)
            sys.exit()
