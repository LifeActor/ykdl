#!/usr/bin/env python
# -*- coding: utf-8 -*-

from logging import getLogger

from ykdl.compact import compact_isstr

class VideoExtractor():
    def __init__(self):
        self.logger = getLogger(self.name)
        self.url = None
        self.vid = None

    def parser(self, url):
        self.__init__()
        if compact_isstr(url) and url.startswith('http'):
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
        if not video_list:
            raise NotImplementedError(u'playlist not support for {} with url: {}'.format(self.name, self.url))
        for video in video_list:
            yield self.parser(video)

    def __getattr__(self, attr):
        return None

    def prepare(self):
        pass

    def extractor(self):
        pass

    def prepare_list(self):
        pass
