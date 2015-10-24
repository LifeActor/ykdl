#!/usr/bin/env python

from .common import match1, download_urls, download_one_url
from .util import log
from .util.wrap import launch_player

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

        self.prepare()

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

    def p_stream(self, stream_id):
        stream = self.streams[stream_id]
        if 'itag' in stream:
            print("    - itag:          %s" % log.sprint(stream_id, log.NEGATIVE))
        else:
            print("    - format:        %s" % log.sprint(stream_id, log.NEGATIVE))

        if 'container' in stream:
            print("      container:     %s" % stream['container'])

        if 'video_profile' in stream:
            print("      video-profile: %s" % stream['video_profile'])

        if 'quality' in stream:
            print("      quality:       %s" % stream['quality'])

        if 'size' in stream:
            print("      size:          %s MiB (%s bytes)" % (round(stream['size'] / 1048576, 1), stream['size']))

        if 'itag' in stream:
            print("    # download-with: %s" % log.sprint("you-get --itag=%s [URL]" % stream_id, log.UNDERLINE))
        else:
            print("    # download-with: %s" % log.sprint("you-get --format=%s [URL]" % stream_id, log.UNDERLINE))

        print()

    def p(self, stream_id=None):
        print("site:                %s" % self.__class__.name)
        print("title:               %s" % self.title)
        if stream_id:
            # Print the stream
            print("stream:")
            self.p_stream(stream_id)

        elif stream_id is None:
            # Print stream with best quality
            print("stream:              # Best quality")
            stream_id = self.stream_types[0]
            self.p_stream(stream_id)

        elif stream_id == []:
            # Print all available streams
            print("streams:             # Available quality and codecs")
            for stream in self.stream_types:
                self.p_stream(stream)

        if self.audiolang:
            print("audio-languages:")
            for i in self.audiolang:
                print("    - lang:          {}".format(i['lang']))
                print("      download-url:  {}\n".format(i['url']))

    def download(self, **kwargs):
        stream_id = self.param.stream_id or self.stream_types[0]
        if self.param.info_only:
            self.p([])
        else:
            self.p(stream_id=stream_id)
            urls = self.streams[stream_id]['src']
            if not urls:
                log.wtf('[Failed] Cannot extract video source.')
            if self.param.player:
                launch_player(self.param.player, urls)
            else:
                download_urls(urls, self.title, self.streams[stream_id]['container'], self.streams[stream_id]['size'], output_dir=self.param.output_dir)


    def download_iter(self, **kwargs):
        stream_id = self.param.stream_id or self.stream_types[0]
        if self.param.info_only:
            self.p([])
        else:
            self.p(stream_id=stream_id)
            i = 0
            for url in self.extract_iter(**kwargs):
                if self.param.player:
                    launch_player(self.param.player, url)
                else:
                    download_one_url(url, self.title, self.streams[stream_id]['container'], output_dir=self.param.output_dir, index = i)
                i += 1
