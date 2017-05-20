#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .youku import Youku

class Tudou(Youku):
    name = u"Tudou (土豆)"

    def __init__(self):
        Youku.__init__(self)
        self.ccode = '0402'

site = Tudou()
