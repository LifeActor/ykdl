#!/usr/bin/env python

from .common import match1, download_urls, parse_host, set_proxy, unset_proxy, download_one_url
from .util import log

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

    def download_by_url(self, url, **kwargs):
        self.url = url
        self.vid= None
        self.stream_types = []

        if 'extractor_proxy' in kwargs and kwargs['extractor_proxy']:
            set_proxy(parse_host(kwargs['extractor_proxy']))
        self.prepare(**kwargs)
        if 'extractor_proxy' in kwargs and kwargs['extractor_proxy']:
            unset_proxy()

        if self.iterable:
            self.download_iter(**kwargs)
        else:
            self.extract(**kwargs)
            self.download(**kwargs)

    def download_by_vid(self, vid, **kwargs):
        self.url = None
        self.vid = vid
        self.stream_types = []

        if 'extractor_proxy' in kwargs and kwargs['extractor_proxy']:
            set_proxy(parse_host(kwargs['extractor_proxy']))
        self.prepare(**kwargs)
        if 'extractor_proxy' in kwargs and kwargs['extractor_proxy']:
            unset_proxy()

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

    def p_i(self, stream_id):
        stream = self.streams[stream_id]
        print("    - title:         %s" % self.title)
        print("       size:         %s MiB (%s bytes)" % (round(stream['size'] / 1048576, 1), stream['size']))
        print("        url:         %s" % self.url)
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

    def p_playlist(self, stream_id=None):
        print("site:                %s" % self.__class__.name)
        print("playlist:            %s" % self.title)
        print("videos:")

    def download(self, **kwargs):
        if 'info_only' in kwargs and kwargs['info_only']:
            if 'stream_id' in kwargs and kwargs['stream_id']:
                # Display the stream
                stream_id = kwargs['stream_id']
                if 'index' not in kwargs:
                    self.p(stream_id)
                else:
                    self.p_i(stream_id)
            else:
                # Display all available streams
                if 'index' not in kwargs:
                    self.p([])
                else:
                    stream_id = self.stream_types[0]
                    self.p_i(stream_id)

        else:
            if 'stream_id' in kwargs and kwargs['stream_id']:
                # Download the stream
                stream_id = kwargs['stream_id']
            else:
                # Download stream with the best quality
                stream_id = self.stream_types[0]

            if 'index' not in kwargs:
                self.p(stream_id)
            else:
                self.p_i(stream_id)

            urls = self.streams[stream_id]['src']
            if not urls:
                log.wtf('[Failed] Cannot extract video source.')
            # For legacy main()
            download_urls(urls, self.title, self.streams[stream_id]['container'], self.streams[stream_id]['size'], output_dir=kwargs['output_dir'])
            # For main_dev()
            #download_urls(urls, self.title, self.streams[stream_id]['container'], self.streams[stream_id]['size'])

    def download_iter(self, **kwargs):
        if 'info_only' in kwargs and kwargs['info_only']:
            if 'stream_id' in kwargs and kwargs['stream_id']:
                # Display the stream
                stream_id = kwargs['stream_id']
                if 'index' not in kwargs:
                    self.p(stream_id)
                else:
                    self.p_i(stream_id)
            else:
                # Display all available streams
                if 'index' not in kwargs:
                    self.p([])
                else:
                    stream_id = self.stream_types[0]
                    self.p_i(stream_id)

        else:
            if 'stream_id' in kwargs and kwargs['stream_id']:
                # Download the stream
                stream_id = kwargs['stream_id']
            else:
                # Download stream with the best quality
                stream_id = self.stream_types[0]

            if 'index' not in kwargs:
                self.p(stream_id)
            else:
                self.p_i(stream_id)

            i = 0
            for url in self.extract_iter(**kwargs):
                download_one_url(url, self.title, self.streams[stream_id]['container'], output_dir=kwargs['output_dir'], index = i)
                i += 1
