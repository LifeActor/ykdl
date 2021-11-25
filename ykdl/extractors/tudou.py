# -*- coding: utf-8 -*-

from ._common import *
from .youku import Youku

class Tudou(Youku):
    name = 'Tudou (土豆)'

    def prepare(self):
        if match1(self.url, '(new-play|video)\.tudou\.com/') is None:
            self.url = get_location(self.url)
        return Youku.prepare(self)

site = Tudou()
