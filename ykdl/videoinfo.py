#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import datetime
import random
from html import unescape
from urllib.parse import unquote
from ykdl.util.fs import legitimize
from ykdl.util import log

class VideoInfo():
    def __init__(self, site, live=False):
        self.site = site
        self._title = None
        self._artist = None
        self.stream_types = []
        self.streams = {}
        self.live = live
        self.subtitles = []
        self.extra = {k: '' for k in ['ua',
                                      'referer',
                                      'header',
                                      'proxy',
                                      'rangefetch'
                                     ]}

    @property
    def title(self):
        if self._title is None:
            return
        title = unquote(unescape(self._title))
        if title != self._title:
            self._title = title
        return title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def artist(self):
        if self._artist is None:
            return
        artist = unquote(unescape(self._artist))
        if artist != self._artist:
            self._artist = artist
        return artist

    @artist.setter
    def artist(self, value):
        self._artist = value

    def print_stream_info(self, stream_id, show_all=False):
        stream = self.streams[stream_id]
        print('    - format:        %s' % log.sprint(stream_id, log.NEGATIVE))
        if 'container' in stream:
            print('      container:     %s' % stream['container'])
        if 'video_profile' in stream:
            print('      video-profile: %s' % stream['video_profile'])
        if 'quality' in stream:
            print('      quality:       %s' % stream['quality'])
        if 'size' in stream and stream['size'] != 0 and stream['size'] != float('inf'):
            print('      size:          %s MiB (%s bytes)' % (round(stream['size'] / 1048576, 1), stream['size']))
        print('    # download-with: %s' % log.sprint('ykdl --format=%s [URL]' % stream_id, log.UNDERLINE))
        if show_all:
            print('Real urls:')
            for url in stream['src']:
                print(url)

    def print_subtitle_info(self, subtitle, show_all=False):
        print('    - language:      %s' % log.sprint(subtitle['lang'], log.NEGATIVE))
        if 'name' in subtitle:
            print('      name:          %s' % subtitle['name'])
        print('      format:        %s' % subtitle['format'])
        size = subtitle.get('size')
        if size and size != float('inf'):
            print('      size:          %s KiB (%s bytes)' % (round(size / 1024, 1), size))
        if show_all:
            print('Real url:')
            print(subtitle['src'])

    def jsonlize(self):
        json_dict = { 'site'   : self.site,
                      'title'  : self.title,
                      'artist'    : self.artist,
                    }
        json_dict['streams'] = self.streams
        json_dict['stream_types'] = self.stream_types
        json_dict['subtitles'] = self.subtitles
        json_dict['extra'] = self.extra
        for s in json_dict['streams']:
            if json_dict['streams'][s].get('size') == float('inf'):
                json_dict['streams'][s].pop('size')
        return json_dict

    def print_info(self, stream_id=None, show_all=False):
        print('site:                %s' % self.site)
        print('title:               %s' % self.title)
        print('artist:              %s' % self.artist)
        print('streams:')
        if not show_all:
            stream_id = stream_id or self.stream_types[0]
            self.print_stream_info(stream_id, show_all)
        else:
            for stream_id in self.stream_types:
                self.print_stream_info(stream_id, show_all)
        if self.subtitles:
            print('subtitles:')
            for subtitle in self.subtitles:
                self.print_subtitle_info(subtitle, show_all)

    def build_file_name(self, stream_id):
        if not self.title:
            self.title = self.site + str(random.randint(1, 9999))
        unique_suffixes = []
        if not stream_id == 'current':
            unique_suffixes.append(stream_id)
        if self.live:
            unique_suffixes.append(legitimize(datetime.datetime.now().isoformat()))
        if unique_suffixes:
            unique_suffix = '_'.join(unique_suffixes)
            return '_'.join([legitimize(self.title, trim= 81 - len(unique_suffix)), unique_suffix])
        else:
            return legitimize(self.title)
