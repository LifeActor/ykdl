#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

def get_extractor(url):
    if re.search("cc.163", url):
        from . import live as s
    elif re.search("music.163", url):
        from . import music as s
        return s.get_extractor(url)
    else:
        from . import video as s
    return s.site
