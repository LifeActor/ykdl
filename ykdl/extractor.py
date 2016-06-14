#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from .util.download import save_url, save_urls
from .util import log
from .util.wrap import launch_player, launch_ffmpeg
from .util.fs import legitimize
from ykdl.util.m3u8_wrap import load_m3u8, load_live_m3u8, live_m3u8_lenth

import sys
import datetime

class VideoExtractor():
    def __init__(self):
        self.url = None
        self.vid = None
        self.param = None
        self.password_protected = False
        self.iterable = False
        self.title = None
        self.artist = None
        self.stream_types = []
        self.streams = {}
        self.live = False


    def print_stream_info(self, stream_id):
        stream = self.streams[stream_id]
        print("    - format:        %s" % log.sprint(stream_id, log.NEGATIVE))
        if 'container' in stream:
            print("      container:     %s" % stream['container'])
        if 'video_profile' in stream:
            print("      video-profile: %s" % stream['video_profile'])
        if 'quality' in stream:
            print("      quality:       %s" % stream['quality'])
        if 'size' in stream:
            print("      size:          %s MiB (%s bytes)" % (round(stream['size'] / 1048576, 1), stream['size']))
        print("    # download-with: %s" % log.sprint("ykdl --format=%s [URL]" % stream_id, log.UNDERLINE))
        if self.param.url:
            print("Real urls:")
            if self.iterable:
                for url in self.extract_iter():
                    print("%s" % url)
            else:
                for url in stream['src']:
                    print("%s" % url)

    def jsonlize(self):
        json_dict = { 'site'   : self.name,
                      'title'  : self.title,
                      'url'    : self.url,
                      'vid'    : self.vid
                    }
        if self.param.info:
            json_dict['streams'] = self.streams
        else:
            stream_id = self.param.format or self.stream_types[0]
            json_dict['streams'] = self.streams[stream_id]
        return json_dict

    def print_info(self):
        print("site:                %s" % self.name)
        print("title:               %s" % self.title)
        print("artist:              %s" % self.artist)
        print("streams:")
        if not self.param.info:
            stream_id = self.param.format or self.stream_types[0]
            self.print_stream_info(stream_id)
        else:
            for stream_id in self.stream_types:
                self.print_stream_info(stream_id)

    def download(self, url, param):
        self.__init__()
        if isinstance(url, str) and url.startswith('http'):
            self.url = url
        else:
            self.vid= url

        self.param = param
        self.stream_types = []

        self.prepare()

        if not self.title:
            t = self.vid or self.url[-5:]
            self.title = self.name + '_' + t

        if self.iterable:
            self.download_iter()
        else:
            self.download_normal()

    def prepare(self):
        pass
        #raise NotImplementedError()

    def extract(self):
        pass
        #raise NotImplementedError()

    def extract_iter(self):
        pass

    def name_suffix(self):
        if self.live:
            return datetime.datetime.now().isoformat()
        else:
            return ''

    def download_normal(self):
        self.extract()
        stream_id = self.param.format or self.stream_types[0]
        if self.param.json:
            print(json.dumps(self.jsonlize(), indent=4, sort_keys=True, ensure_ascii=False))
        else:
            self.print_info()
        if self.param.info or self.param.url:
            return
        urls = self.streams[stream_id]['src']
        if not urls:
            raise RuntimeError(self.name+ ': [Failed] Cannot extract video source from: ' + self.url if self.url else str(self.vid))
        elif self.param.player:
            launch_player(self.param.player, urls)
        else:
            name_list = [self.title]
            if not stream_id == 'current':
                name_list.append(stream_id)
            if self.name_suffix():
                name_list.append(self.name_suffix())
            name = legitimize('_'.join(name_list))
            if self.streams[stream_id]['container'] == 'm3u8':
                self.streams[stream_id]['container'] = 'ts'
                if self.live:
                    urls = load_live_m3u8(urls[0])
                else:
                    urls = load_m3u8(urls[0])
            save_urls(urls, name, self.streams[stream_id]['container'])
            lenth = 0
            if type(urls) is list:
                lenth = len(urls)
            else: #generator
                lenth = live_m3u8_lenth()
            if self.param.merge and lenth > 1:
                launch_ffmpeg(name,  self.streams[stream_id]['container'], lenth)


    def download_iter(self):
        stream_id = self.param.format or self.stream_types[0]
        if self.param.json:
            print(json.dumps(self.jsonlize(), indent=4, sort_keys=True, ensure_ascii=False))
        else:
            self.print_info()
        if self.param.info or self.param.url:
            return
        i = 0
        name_list = [self.title]
        if not stream_id == 'current':
            name_list.append(stream_id)
        if self.name_suffix():
            name_list.append(self.name_suffix())
        for url in self.extract_iter():
            if self.param.player:
                launch_player(self.param.player, [url])
            else:
                print("Download: " + self.title + " part %d" % i)
                save_url(url, name + '_%d_.' % i + self.streams[stream_id]['container'])
                print("")
                i += 1
        if self.param.merge and i > 1:
            launch_ffmpeg(name,  self.streams[stream_id]['container'], i)

    def prepare_list(self):
        pass

    def download_playlist(self, url, param):
        self.url = url
        video_list = self.prepare_list()
        if not video_list:
            raise NotImplementedError('Playlist is not supported for ' + self.name)
        for v in video_list[param.start:]:
            self.download(v, param)
