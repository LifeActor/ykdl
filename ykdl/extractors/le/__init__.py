#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

def get_extractor(url):
    if re.search("lunbo", url):
        from . import lunbo as s
    elif re.search("finance", url):
        from . import finance as s
    elif re.search("bcloud", url):
        from . import letvcloud as s
    else:
        from . import le as s
    return s.site
