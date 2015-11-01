#!/usr/bin/env python

from .common import match1, download_urls, download_one_url
from .util import log
from .util.wrap import launch_player
import json

class VideoExtractor():
    def __init__(self, *args):
        self.url = None
        self.title = None
        self.vid = None
        self.streams = {}
        self.audiolang = None
        self.password_protected = False
        self.iterable = False
        self.stream_types = []

        if args:
            self.url = args[0]

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
                for url in self.extract_iter(**kwargs):
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
        string += "streams:\n"
        if not self.param.info_only:
            stream_id = self.param.stream_id or self.stream_types[0]
            string += self.stream_to_string(stream_id)
        else:
            for stream_id in self.stream_types:
                string += self.stream_to_string(stream_id)

        if self.audiolang:
            string += "audio-languages:\n"
            for i in self.audiolang:
                string +="    - lang:          {}\n".format(i['lang'])
                string +="      download-url:  {}\n".format(i['url'])
        return string

    def download_by_url(self, url, param, **kwargs):
        self.param = param
        self.url = url
        self.vid= None
        self.stream_types = []

        self.prepare(**kwargs)

        if self.iterable:
            self.download_iter(**kwargs)
        else:
            self.extract(**kwargs)
            self.download(**kwargs)

    def download_by_vid(self, vid, param, **kwargs):
        self.param = param
        self.url = None
        self.vid = vid
        self.stream_types = []

        self.prepare(**kwargs)

        if self.iterable:
            self.download_iter(**kwargs)
        else:
            self.extract(**kwargs)
            self.download(**kwargs)

    def prepare(self, **kwargs):
        pass
        #raise NotImplementedError()

    def extract(self, **kwargs):
        pass
        #raise NotImplementedError()

    def extract_iter(**kwargs):
        pass

    def download(self, **kwargs):
        stream_id = self.param.stream_id or self.stream_types[0]
        print(self)
        if self.param.info_only or self.param.dry_run:
            return
        urls = self.streams[stream_id]['src']
        if not urls:
            log.wtf('[Failed] Cannot extract video source.')
        elif self.param.player:
            launch_player(self.param.player, urls)
        else:
            download_urls(urls, self.title, self.streams[stream_id]['container'], self.streams[stream_id]['size'], output_dir=self.param.output_dir)


    def download_iter(self, **kwargs):
        stream_id = self.param.stream_id or self.stream_types[0]
        print(self)
        if self.param.info_only or self.param.dry_run:
            return
        i = 0
        for url in self.extract_iter(**kwargs):
            if self.param.player:
                launch_player(self.param.player, url)
            else:
                download_one_url(url, self.title, self.streams[stream_id]['container'], output_dir=self.param.output_dir, index = i)
                i += 1
