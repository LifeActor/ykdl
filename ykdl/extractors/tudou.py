#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .youku import Youku
from ykdl.util.html import get_location, add_header
import re

class Tudou(Youku):
    name = u"Tudou (土豆)"

    def __init__(self):
        Youku.__init__(self)
        self.referer = "http://video.tudou.com/"
        
        self.ccode = '0505'

    def prepare(self):
        if not re.search('video.tuodou.com', self.url):
            self.url = get_location(self.url)
        return Youku.prepare(self)

site = Tudou()
