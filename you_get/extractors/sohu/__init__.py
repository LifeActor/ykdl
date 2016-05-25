#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

def get_extractor(url):

    if re.search('my.tv.sohu.com', url):
        from . import my as s
        return s.site
    else:
        from . import tv as s
        return s.site
    raise NotImplementedError(url)
 
