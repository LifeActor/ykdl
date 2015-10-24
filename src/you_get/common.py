#!/usr/bin/env python

import getopt
import json
import locale
import os
import platform
import re
import sys
from urllib import request, parse
from importlib import import_module

from .version import __version__
from .util import log
from .util.strings import get_filename, unescape_html
from .util.progressbar import SimpleProgressBar, PiecesProgressBar
from .util.match import match1, matchall, r1
from .util.html import *
from .util.download import *
from .param import Param

def playlist_not_supported(name):
    def f(*args, **kwargs):
        raise NotImplementedError('Playlist is not supported for ' + name)
    return f

alias = {
        '163': 'netease',
        'fun': 'funshion',
        'iask': 'sina',
        'in': 'alive',
        'kankanews': 'bilibili',
        'smgbb': 'bilibili',
        'weibo': 'miaopai',
        '7gogo': 'nanagogo'
}
def url_to_module(url):
    video_host = match1(url, 'https?://([^/]+)/')
    video_url = match1(url, 'https?://[^/]+(.*)')
    assert video_host and video_url, 'invalid url: ' + url

    if video_host.endswith('.com.cn'):
        video_host = video_host[:-3]
    domain = match1(video_host, '(\.[^.]+\.[^.]+)$') or video_host
    assert domain, 'unsupported url: ' + url

    k = match1(domain, '([^.]+)')
    if k in alias.keys():
        k = alias[k]
    try:
        m = import_module('.'.join(['you_get','extractors', k]))
        return m
    except(SyntaxError):
        log.wtf("SyntaxError in module {}".format(k))
    except:
        import http.client
        conn = http.client.HTTPConnection(video_host)
        conn.request("HEAD", video_url)
        res = conn.getresponse()
        location = res.getheader('location')
        if location is None:
            return import_module('you_get.extractors.generalembed')
        elif location != url:
            return url_to_module(location)
        else:
            raise ConnectionResetError(url)

def main():

    para = Param(sys.argv[1:])

    for url in para.urls:
        m = url_to_module(url)
        if para.playlist:
            m.download_playlist(url, para)
        else:
            m.download(url, para)
