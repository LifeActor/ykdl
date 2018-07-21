#!/usr/bin/env python
# -*- coding: utf-8 -*-

from importlib import import_module
from logging import getLogger
from .common import alias

class EmbedExtractor():
    """
    this class is to help video embed site to handle
    video from other site.
    we just need to know the source site name, and video ID
    that's enough.
    with site name and VID, develop can easily to find out the real URL

    because embed site don't have video info, so they don't need stream_info.
    """

    def __init__(self):
        self.video_info = None
        self.logger = getLogger(self.name)

    def prepare(self):
        """
        this API is to do real job to get site and VID
        sometimes title
        MUST override!!
        """
        pass

    def prepare_playlist(self):
        """
        this API is to do real job to get site and VID
        sometimes title
        MUST override!!
        """
        pass

    def parser(self, url):
        if isinstance(url, str) and url.startswith('http'):
            self.url = url
        self.video_info = None
        self.prepare()

        if not self.video_info:
            raise NotImplementedError(self.url + " is not supported")

        site, vid = self.video_info
        if site in alias.keys():
            site = alias[site]
        s = import_module('.'.join(['ykdl','extractors',site])).site
        return s.parser(vid)

    def parser_list(self, url):
        if isinstance(url, str) and url.startswith('http'):
            self.url = url
        self.video_info_list = []
        self.prepare_playlist()

        if not self.video_info_list:
            raise NotImplementedError('Playlist is not supported for ' + self.name + 'with url: ' + self.url)

        info_list = []
        for v in self.video_info_list:
            site, vid = v
            if site in alias.keys():
                site = alias[site]
            s = import_module('.'.join(['ykdl','extractors',site])).site
            yield s.parser(vid)

    def __getattr__(self, attr):
        return None
