#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .youkubase import YoukuBase
from ..util.html import get_content
from .youkujs import install_acode
import json

class Acorig(YoukuBase):
    name = u"AcFun 优酷合作视频"

    client_id = '908a519d032263f8'
    ct = 86

    def setup(self):

        if not self.title:
            self.title = self.name + "-" + self.vid

        self.vid = json.loads(get_content('http://www.acfun.tv/video/getVideo.aspx?id={}'.format(self.vid)))['sourceId']
        install_acode('v', 'b', '1z4i', '86rv', 'ogb', 'ail')
        self.get_custom_sign()
        self.get_custom_stream()


site = Acorig()
