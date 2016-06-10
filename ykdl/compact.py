#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
if sys.version_info[0] == 3:
    from urllib.request import Request, urlopen, HTTPSHandler, build_opener, HTTPCookieProcessor, install_opener, ProxyHandler
    from urllib.parse import urlencode, urlparse
    from http.client import HTTPConnection
    compact_str = str
    compact_bytes = bytes
    from urllib.parse import unquote as compact_unquote
    from tempfile import NamedTemporaryFile as compact_tempfile
else:
    from urllib2 import Request, urlopen, HTTPSHandler, build_opener, HTTPCookieProcessor, install_opener, ProxyHandler
    from urllib import urlencode
    from urlparse import urlparse
    from httplib import HTTPConnection
    compact_str = unicode
    def compact_bytes(string, encode):
        return string

    def compact_unquote(string, encoding = 'utf-8'):
        from urllib import unquote
        return unquote(str(string)).decode(encoding)

    from tempfile import NamedTemporaryFile
    __tmp__ = []
    import codecs
    def compact_tempfile(mode='w+b', buffering=-1, encoding=None, newline=None, suffix='', prefix='tmp', dir=None, delete=True):
        tmp = NamedTemporaryFile(mode=mode, suffix=suffix, prefix=prefix, dir=dir, delete=delete)
        __tmp__.append(tmp)
        return codecs.open(tmp.name, mode, encoding)
