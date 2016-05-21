#!/usr/bin/env python3

import re

def get_extractor(url):
    if re.search("music.baidu", url):
        from . import music as s
        return s.site
    raise NotImplementedError(url)
