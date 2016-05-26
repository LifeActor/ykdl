#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
if sys.version_info[0] == 3:
    from urllib.request import Request, urlopen, HTTPSHandler, build_opener, HTTPCookieProcessor, install_opener
    from urllib.parse import unquote, urlencode, urlparse
    from http.client import HTTPConnection
else:
    from urllib2 import Request, urlopen, HTTPSHandler, build_opener, HTTPCookieProcessor, install_opener
    from urllib import urlencode, unquote
    from urlparse import urlparse
    from httplib import HTTPConnection
