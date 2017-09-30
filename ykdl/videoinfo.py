#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import json
import sys
import datetime
import random
from ykdl.util.fs import legitimize
from ykdl.util import log

class FallbackDict(dict):
    fallback = {}
    fall_to_anyone = False
    fallback_tip = 'Dict key fallback {fkey!r} applied to {key!r}.'

    def _print_tip(self, key, fkey):
        print(self.fallback_tip.format(key=key, fkey=fkey))

    def get_fallback(self, key, print_tip=False):
        keys = []
        while True:
            if key in self:
                if keys:
                    if print_tip:
                        self._print_tip(keys[0], key)
                    return True, key
                else:
                    return False, None
            else:
                keys.append(key)
                key_fallback = self.fallback.get(key)
                if key_fallback:
                    key = key_fallback
                elif self.fall_to_anyone and self:
                    for key, _ in self.items():
                        if print_tip:
                            self._print_tip(keys[0], key)
                        return True, key
                else:
                    return None, keys

    def __getitem__(self, key):
        hit, key_fallback = self.get_fallback(key, True)
        if hit:
            return dict.__getitem__(self, key_fallback)
        elif hit is False:
            return dict.__getitem__(self, key)
        else:
            raise KeyError(key_fallback, 'Fallback failed.')

    def get(self, key, value=None):
        try:
            return self[key]
        except KeyError:
            return value

ids = ('4k', 'BD', 'TD', 'HD', 'SD', 'LD', 'current') # 'Phone' in longzhu.py is?
ids_fallback = {}
for i in range(0, len(ids) - 1):
    ids_fallback[ids[i]] = ids[i + 1]

class IdsFallbackDict(FallbackDict):
    fallback = ids_fallback
    fallback_tip = 'Format fallback {fkey!r} applied to {key!r}.'

class VideoInfo():
    def __init__(self, site, live = False):
        self.site = site
        self.title = None
        self.artist = None
        self.stream_types = []
        self.streams = IdsFallbackDict()
        self.live = live
        self.extra = {"ua": "", "referer": ""}

    def print_stream_info(self, stream_id, show_all = False):
        hit, stream_id_fallback = self.streams.get_fallback(stream_id, True)
        if hit:
            stream_id = stream_id_fallback
        stream = self.streams[stream_id]
        print("    - format:        %s" % log.sprint(stream_id, log.NEGATIVE))
        if 'container' in stream:
            print("      container:     %s" % stream['container'])
        if 'video_profile' in stream:
            print("      video-profile: %s" % stream['video_profile'])
        if 'quality' in stream:
            print("      quality:       %s" % stream['quality'])
        if 'size' in stream and stream['size'] != 0 and stream['size'] != float('inf'):
            print("      size:          %s MiB (%s bytes)" % (round(stream['size'] / 1048576, 1), stream['size']))
        print("    # download-with: %s" % log.sprint("ykdl --format=%s [URL]" % stream_id, log.UNDERLINE))
        if show_all:
            print("Real urls:")
            for url in stream['src']:
                print("%s" % url)

    def jsonlize(self):
        json_dict = { 'site'   : self.site,
                      'title'  : self.title,
                      'artist'    : self.artist,
                    }
        json_dict['streams'] = self.streams
        json_dict['stream_types'] = self.stream_types
        json_dict['extra'] = self.extra
        return json_dict

    def print_info(self, stream_id = None, show_all = False):
        print("site:                %s" % self.site)
        print("title:               %s" % self.title)
        print("artist:              %s" % self.artist)
        print("streams:")
        if not show_all:
            stream_id = stream_id or self.stream_types[0]
            self.print_stream_info(stream_id, show_all)
        else:
            for stream_id in self.stream_types:
                self.print_stream_info(stream_id, show_all)

    def build_file_name(self,stream_id):
        if not self.title:
            self.title = self.site + str(random.randint(1, 9999))
        name_list = [self.title]
        if not stream_id == 'current':
            hit, stream_id_fallback = self.streams.get_fallback(stream_id)
            if hit:
                stream_id = '%s(fallback)' % stream_id_fallback
            name_list.append(stream_id)
        if self.live:
            name_list.append(datetime.datetime.now().isoformat())
        return legitimize('_'.join(name_list))
