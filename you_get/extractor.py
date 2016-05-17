#!/usr/bin/env python
import json
import os

from .util.download import save_url, save_urls
from .util import log
from .util.wrap import launch_player
from .util.fs import legitimize



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


    def stream_to_string(self, stream_id):
        stream = self.streams[stream_id]
        string  = "    - format:        %s\n" % log.sprint(stream_id, log.NEGATIVE)
        if 'container' in stream:
            string += "      container:     %s\n" % stream['container']
        if 'video_profile' in stream:
            string += "      video-profile: %s\n" % stream['video_profile']
        if 'quality' in stream:
            string += "      quality:       %s\n" % stream['quality']
        if 'size' in stream:
            string += "      size:          %s MiB (%s bytes)\n" % (round(stream['size'] / 1048576, 1), stream['size'])
        string += "    # download-with: %s\n" % log.sprint("you-get --format=%s [URL]" % stream_id, log.UNDERLINE)
        if self.param.dry_run:
            string += "Real urls:\n"
            if self.iterable:
                for url in self.extract_iter():
                    string += "%s\n" % url
            else:
                for url in stream['src']:
                    string += "%s\n" % url
        return string

    def jsonlize(self):
        json_dict = { 'site'   : self.name,
                      'title'  : self.title,
                      'url'    : self.url,
                      'vid'    : self.vid
                    }
        if self.param.info_only:
            json_dict['streams'] = self.streams
        else:
            stream_id = self.param.stream_id or self.stream_types[0]
            json_dict['streams'] = self.streams[stream_id]
        return json_dict

    def __str__(self):
        if self.param.json_out:
            return json.dumps(self.jsonlize(), indent=4, sort_keys=True, ensure_ascii=False)
        string  = "site:                %s\n" % self.name
        string += "title:               %s\n" % self.title
        string += "artist:              %s\n" % self.artist
        string += "streams:\n"
        if not self.param.info_only:
            stream_id = self.param.stream_id or self.stream_types[0]
            string += self.stream_to_string(stream_id)
        else:
            for stream_id in self.stream_types:
                string += self.stream_to_string(stream_id)

        return string

    def download(self, url, param):
        if isinstance(url, str) and url.startswith('http'):
            self.url = url
            self.vid= None
        else:
            self.url = None
            self.vid= url

        self.param = param
        self.stream_types = []
        #mkdir and cd to output dir
        if not self.param.output_dir == '.':
            if not os.path.exists(self.param.output_dir):
                try:
                    os.mkdir(self.param.output_dir)
                except:
                    log.w("No permission or Not found " + param_dict['output_dir'])
                    log.w("use current folder")
                    self.param.output_dir = '.'
        if os.path.exists(self.param.output_dir):
            os.chdir(self.param.output_dir)

        self.prepare()

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

    def download_normal(self):
        self.extract()
        stream_id = self.param.stream_id or self.stream_types[0]
        print(self)
        if self.param.info_only or self.param.dry_run:
            return
        urls = self.streams[stream_id]['src']
        if not urls:
            raise RuntimeError(self.name+ ': [Failed] Cannot extract video source from: ' + self.url if self.url else str(self.vid))
        elif self.param.player:
            launch_player(self.param.player, urls)
        else:
            save_urls(urls, legitimize(self.title), self.streams[stream_id]['container'])


    def download_iter(self):
        stream_id = self.param.stream_id or self.stream_types[0]
        print(self)
        if self.param.info_only or self.param.dry_run:
            return
        i = 0
        for url in self.extract_iter():
            if self.param.player:
                launch_player(self.param.player, [url])
            else:
                print("Download: " + self.title + " part %d" % i)
                save_url(url, legitimize(self.title + '_%02d_.' % i + self.streams[stream_id]['container']))
                print()
                i += 1

    def download_playlist(self, url, param):
        raise NotImplementedError('Playlist is not supported for ' + self.name)
