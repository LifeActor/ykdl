#!/usr/bin/env python3

import re

def get_extractor(url):
    if re.search("live.bili", url):
        from . import live as s
    else:
        from . import video as s
    return s.site
