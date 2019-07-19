#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import json

from ykdl.videoinfo import VideoInfo
from ykdl.extractor import VideoExtractor
from ykdl.util.match import match1
from ykdl.util.html import get_content


class ZHULive(VideoExtractor):
    name = u"Zhuafan"

    def decodeencoded(self, playinfo):
        b = list(base64.b64decode(playinfo))
        t7 = []
        if len(b) > 12:
            if b[0] == 255 and b[1] == 255 and b[2] == 255 and b[3] == 254:
                t2 = b[4]
                t3 = b[5]
                t4 = b[6]
                t5 = b[7]
                t6 = (b[t4 + 8] & 255 ^ t2) << 24 | (b[t4 + 9] & 255 ^ t3) << 16 | (b[t4 + 10] & 255 ^ t2) << 8 | b[
                    t4 + 11] & 255 ^ t3
                if t6 == len(b) - 12 - t4 - t5:
                    t8 = t4 + 12
                    t9 = t6 + 1
                    t7 = [None] * t9
                    while t9 >= 0:
                        if (t9 & 1) == 0:
                            t10 = t2
                        else:
                            t10 = t3
                        try:
                            t7[t9] = (b[t8 + t9] ^ t10)
                        except Exception as e:
                            pass
                        t9 -= 1
                retstr = ""
                i = 0
                while i < len(t7):
                    retstr += chr((int(t7[i])))
                    i += 1
                return retstr[:-1]  # remove last character as it makes json invalid
        return ""

    def prepare(self):
        info = VideoInfo(self.name)
        info.live = True
        if self.url and not self.vid:
            html = get_content(self.url)
            info.title = match1(html, '<div class=\"play-title-inner\">([^<]+)</div>')
            info.artist = match1(html, 'data-director=\"([^\"]+)\"')
            playInfo = match1(html, 'playInfo\s*:\s*"(.*)"')
            decoded = json.loads(self.decodeencoded(playInfo))
            print(decoded["origin"])
            # using only origin, as I have noticed - all links are same
            info.stream_types.append('current')
            info.streams['current'] = {'container': 'flv', 'video_profile': 'current',
                                       'src': [decoded["origin"]], 'size': 0}
        return info


site = ZHULive()
