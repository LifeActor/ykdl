#!/usr/bin/env python
# -*- coding: utf-8 -*-

from importlib import import_module

from .util.html import get_location_and_header
from .extractors import singlemultimedia
import re
import logging

logger = logging.getLogger('common')

alias = {
        '163'    : 'netease',
        'aixifan': 'acfun',
        'amemv'  : 'douyin',
        'cntv'   : 'cctv',
        'douyutv': 'douyu',
        'iask'   : 'sina',
        'letv'   : 'le',
        'wetv'   : 'qq'
}
exclude_list = ['com', 'net', 'org']
def url_to_module(url):
    if not url.startswith('http'):
        logger.warning('> url not starts with http(s) ' + url)
        logger.warning('> assume http connection!')
        url = 'http://' + url
    url_infos = re.match(
            'https?://([.\-\w]*?(?:([\-\w]+)\.)?([\-\w]+)\.[\-\w]+)/.+?(?:\.([^?]+))?(?:\?|$)', url)
    assert url_infos, 'wrong URL string!'
    host, dm3, dm2, ext = url_infos.groups()
    logger.debug('host> ' + host)

    short_name = dm2 in exclude_list and dm3 or dm2
    if short_name in alias.keys():
        short_name = alias[short_name]
    logger.debug('short_name> ' + short_name)
    try:
        m = import_module('.'.join(['ykdl','extractors', short_name]))
        if hasattr(m, 'get_extractor'):
            site, url = m.get_extractor(url)
        else:
            site = m.site
        return site, url
    except(ImportError):
        if ext in singlemultimedia.extNames:
            logger.debug('> the extension name %r match multimedia types', ext)
            logger.debug('> Go SingleMultimedia')
            singlemultimedia.site.resheader = get_location_and_header(url)[1]
            return singlemultimedia.site, url

        logger.debug('> Try HTTP Redirection!')
        new_url, resheader = get_location_and_header(url)
        if new_url == url:
            logger.debug('> NO HTTP Redirection')
            if resheader['Content-Type'].startswith('text/'):
                logger.debug('> Try GeneralSimple')
                from ykdl.extractors.generalsimple import site
                if site.parser(url):
                    return site, url
                logger.debug('> Try GeneralEmbed')
                return import_module('ykdl.extractors.generalembed').site, url
            else:
                logger.debug('> Try SingleMultimedia')
                singlemultimedia.site.resheader = resheader
                return singlemultimedia.site, url
        else:
            logger.debug('> new url ' + new_url)
            return url_to_module(new_url)
