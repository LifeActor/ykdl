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
