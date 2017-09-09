#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

def get_extractor(url):
    if re.search("live.bili", url):
        from . import live as s
    elif re.search("vc.bili", url):
        from . import vc as s
    else:
        from . import video as s
    return s.site
