#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Thread
from time import sleep
import json

from ykdl.util.wrap import launch_player


class Mpvplayer(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.playlist = []
        self.name = 'mpv playback thread'
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
            if not 'args' in obj:
                obj['args'] = {'ua':'', 'header':'', 'title':'', 'referer':''}
            obj['play'] = False
            self.handle = launch_player(obj['urls'], obj['ext'], **obj['args'])
            self.handle.wait()
