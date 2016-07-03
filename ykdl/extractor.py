#!/usr/bin/env python
# -*- coding: utf-8 -*-

class VideoExtractor():
    def __init__(self):
        self.url = None
        self.vid = None

    def parser(self, url):
        self.__init__()
        if isinstance(url, str) and url.startswith('http'):
            self.url = url
        else:
            self.vid= url

        # if info is returned by prepare, no need go extractor
        # else go extractor.
        # info is instance of VideoInfo
        info = self.prepare()
        return info

    def parser_list(self, url):
        self.url = url
        video_list = self.prepare_list()
        return [self.parser(v) for v in video_list]

    def prepare(self):
        pass

    def extractor(self):
        pass

    def prepare_list(self):
        pass
