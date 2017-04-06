#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

def get_extractor(url):
    if re.search("video", url):
        from . import video as s
    elif re.search("news", url):
        from . import news as s
    elif re.search("gongkaike", url):
        from . import gongkaike as s
    return s.site
