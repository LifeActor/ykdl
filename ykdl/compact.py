#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import platform
import struct

if sys.version_info[0] == 3:
    from urllib.request import Request, urlopen, HTTPSHandler, build_opener, HTTPCookieProcessor, install_opener, ProxyHandler
    from urllib.parse import urlencode, urlparse
    from http.client import HTTPConnection
    compact_str = str
    compact_bytes = bytes
    from urllib.parse import unquote as compact_unquote
    from tempfile import NamedTemporaryFile
    def compact_tempfile(mode='w+b', encoding=None, suffix='', prefix='tmp', dir=None):
        if platform.system() == 'Windows':
            _del_  = False
        else:
            _del_  = True
        return NamedTemporaryFile(mode=mode, encoding=encoding, suffix=suffix, prefix=prefix, dir=dir, delete=_del_)
    def compact_isstr(s):
        return isinstance(s, str)
else:
    from urllib2 import Request, urlopen, HTTPSHandler, build_opener, HTTPCookieProcessor, install_opener, ProxyHandler
    from urllib import urlencode
    from urlparse import urlparse
    from httplib import HTTPConnection
    import types
    compact_str = unicode
    def compact_bytes(string, encode):
        return string.encode(encode)

    def compact_unquote(string, encoding = 'utf-8'):
        from urllib import unquote
        return unquote(str(string)).decode(encoding)

    from tempfile import NamedTemporaryFile
    __tmp__ = []
    import codecs
    def compact_tempfile(mode='w+b', encoding=None, suffix='', prefix='tmp', dir=None):
        if platform.system() == 'Windows':
            _del_  = False
        else:
            _del_  = True
        tmp = NamedTemporaryFile(mode=mode, suffix=suffix, prefix=prefix, dir=dir, delete=_del_)
        __tmp__.append(tmp)
        return codecs.open(tmp.name, mode, encoding)
    def compact_isstr(s):
        return isinstance(s, types.UnicodeType) or isinstance(s, str)

try:
    struct.pack('!I', 0)
except TypeError:
    # In Python 2.6 and 2.7.x < 2.7.7, struct requires a bytes argument
    # See https://bugs.python.org/issue19099
    def compat_struct_pack(spec, *args):
        if isinstance(spec, compat_str):
            spec = spec.encode('ascii')
        return struct.pack(spec, *args)

    def compat_struct_unpack(spec, *args):
        if isinstance(spec, compat_str):
            spec = spec.encode('ascii')
        return struct.unpack(spec, *args)
else:
    compat_struct_pack = struct.pack
    compat_struct_unpack = struct.unpack

def tmp_null():
    if platform.system() == 'Windows':
        null = 'nul'
    else:
        null = '/dev/null'
    return open(null, 'w')

compact_dev_null = tmp_null()
del tmp_null
