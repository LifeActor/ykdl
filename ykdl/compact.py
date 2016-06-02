#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
if sys.version_info[0] == 3:
    from urllib.request import Request, urlopen, HTTPSHandler, build_opener, HTTPCookieProcessor, install_opener, ProxyHandler
    from urllib.parse import unquote, urlencode, urlparse
    from http.client import HTTPConnection
    compact_str = str
else:
    from urllib2 import Request, urlopen, HTTPSHandler, build_opener, HTTPCookieProcessor, install_opener, ProxyHandler
    from urllib import urlencode, unquote
    from urlparse import urlparse
    from httplib import HTTPConnection
    compact_str = unicode
