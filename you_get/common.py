#!/usr/bin/env python

import sys
from importlib import import_module

from .util.match import match1
from .util.html import fake_headers
from .param import arg_parser
from .util import log

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
        m = import_module('.'.join(['you_get','extractors', k]))
        if hasattr(m, "get_extractor"):
            site = m.get_extractor(url)
        else:
            site = m.site
        return site, url
    except(SyntaxError):
        raise
    except(NotImplementedError):
        raise
    except:
        import http.client
        conn = http.client.HTTPConnection(video_host)
        conn.request("HEAD", video_url, headers=fake_headers)
        res = conn.getresponse()
        location = res.getheader('location')
        if location is None:
            return import_module('you_get.extractors.generalembed').site, url
        elif location != url:
            return url_to_module(location)
        else:
            raise ConnectionResetError(url)

def main():
    args = arg_parser()
    for url in args.video_urls:
        try:
            m,u = url_to_module(url)
            if not u == url:
                args.video_urls[args.video_urls.index(url)]  = u
            if args.playlist:
                m.download_playlist(u, args)
            else:
                m.download(u, args)
        except AssertionError as e:
            log.wtf(str(e))
        except RuntimeError as e:
            log.e(str(e))
        except NotImplementedError as e:
            log.e(str(e))
