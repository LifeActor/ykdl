#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Thread
import subprocess
from time import sleep
import json

def launch_player(urls, **args):

    cmd = ['mpv']
    cmd += ['--no-ytdl', '--demuxer-lavf-o', 'protocol_whitelist=[file,tcp,http]']
    if len(urls) > 1:
        cmd += ['--merge-files']
    if args['ua']:
        cmd += ['--user-agent', args['ua']]
    if args['referer']:
        cmd += ['--referrer', args['referer']]
    if args['title']:
        cmd += ['--force-media-title', args['title']]
    if args['header']:
        cmd += ['--http-header-fields', args['header']]
    cmd += list(urls)
    return subprocess.Popen(cmd)


class Mpvplayer(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.playlist = []
        self.name = "mpv playback thread"
        self.handle = None
        self.__exit__ = False
    def play(self, obj):
        self.playlist.append(obj)
        return 0
    def stop(self):
        if self.handle:
            self.handle.terminate()
    def exit(self):
        self.__exit__ = True
        self.stop()
    def run(self):
        while not self.__exit__:
            if len(self.playlist) == 0:
                sleep(10)
                continue
            o = self.playlist[0]
            self.playlist.remove(o)
            obj = json.loads(o)
            if not "args" in obj:
                obj["args"] = {"ua":"", "header":"", "title":"", "referer":""}
            self.handle = launch_player(obj["urls"], **obj["args"])
            self.handle.wait()
