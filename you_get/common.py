#!/usr/bin/env python

import sys
from urllib import request
from importlib import import_module

from .util.match import match1
from .util.html import fake_headers
from .param import Param

def mime_to_container(mime):
    mapping = {
        'video/3gpp': '3gp',
        'video/mp4': 'mp4',
        'video/webm': 'webm',
        'video/x-flv': 'flv',
    }
    if mime in mapping:
        return mapping[mime]
    else:
        return mime.split('/')[1]

alias = {
        '163': 'netease',
        'fun': 'funshion',
        'iask': 'sina',
        'in': 'alive',
        'kankanews': 'bilibili',
        'smgbb': 'bilibili',
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
        m = import_module('.'.join(['you_get','extractors', k])).site
        return m, url
    except(SyntaxError):
        raise
    except:
        res = request.urlopen(request.Request(url, headers = fake_headers))
        location = res.geturl()
        if location is None:
            return import_module('you_get.extractors.generalembed').site, url
        elif location != url:
            return url_to_module(location)
        else:
            raise ConnectionResetError(url)

def main():
    para = Param(sys.argv[1:])
    for url in para.urls:
        m,u = url_to_module(url)
        if not u == url:
            para.urls[para.urls.index(url)]  = u
        if para.playlist:
            m.download_playlist(u, para)
        else:
            m.download(u, para)
