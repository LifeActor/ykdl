#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

def get_extractor(url):
    if re.search("live.qq", url):
        from . import live as s
    elif re.search("v.qq", url):
        from . import video as s
    return s.site
