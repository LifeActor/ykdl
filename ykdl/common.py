#!/usr/bin/env python
# -*- coding: utf-8 -*-

from importlib import import_module

from .util.match import match1
from .util.html import fake_headers
import logging

logger = logging.getLogger("common")

alias = {
        '163': 'netease',
        'iask': 'sina',
        'in': 'alive',
        'cntv' : 'cctv',
        'letv' : 'le',
        'douyutv' : 'douyu',
        'aixifan' : 'acfun'
}
exclude_list = ['com', 'net', 'org']
def url_to_module(url):
    if not url.startswith("http"):
        logger.warning("> url not starts with http(s) " + url)
        logger.warning("> assume http connection!")
        url = "http://" + url
    video_host = url.split('/')[2]
    host_list = video_host.split('.')
    if host_list[-2] in exclude_list:
        short_name = host_list[-3]
    else:
        short_name = host_list[-2]
    logger.debug('video_host> ' + video_host)
    logger.debug('short_name> ' + short_name)
    if short_name in alias.keys():
        short_name = alias[short_name]
    try:
        m = import_module('.'.join(['ykdl','extractors', short_name]))
        if hasattr(m, "get_extractor"):
            site = m.get_extractor(url)
        else:
            site = m.site
        return site, url
    except(ImportError):
        logger.debug('> Try HTTP Redirection!')
        from ykdl.compact import HTTPConnection
        conn = HTTPConnection(video_host)
        conn.request("HEAD", url, headers=fake_headers)
        res = conn.getresponse()
        location = res.getheader('location')
        if location is None:
            logger.debug('> NO HTTP Redirection')
            logger.debug('> Go Generalembed')
            return import_module('ykdl.extractors.generalembed').site, url
        else:
            logger.debug('New Location> ' + location)
            return url_to_module(location)
