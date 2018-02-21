#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.util.html import get_content, add_header, fake_headers, get_location
from ykdl.util.match import match1, matchall


def parse_cid_playurl(xml):
    from xml.dom.minidom import parseString
    urls = []
    size = 0
    doc = parseString(xml.encode('utf-8'))
    ext = doc.getElementsByTagName('format')[0].firstChild.nodeValue
    for durl in doc.getElementsByTagName('durl'):
        urls.append(durl.getElementsByTagName('url')[0].firstChild.nodeValue)
        size += int(durl.getElementsByTagName('size')[0].firstChild.nodeValue)
    return urls, size, ext

class BiliBase(VideoExtractor):
    supported_stream_profile = [u'蓝光', u'超清', u'高清', u'流畅']
    profile_2_type = {u'蓝光': 'BD', u'超清': 'TD', u'高清': 'HD', u'流畅' :'SD'}
    fmt_2_profile = {'flv720': u'超清', 'flv480': u'高清', 'hdmp4': u'高清', 'mp4': u'流畅'}

    def prepare(self):
        info = VideoInfo(self.name)
        add_header("Referer", "http://www.bilibili.com")
        info.extra["referer"] = "http://www.bilibili.com"
        info.extra["ua"] = fake_headers['User-Agent']

        self.vid, info.title = self.get_vid_title()

        assert self.vid, "can't play this video: {}".format(self.url)

        for q in self.supported_stream_profile:
            api_url = self.get_api_url(self.supported_stream_profile.index(q))
            html = get_content(api_url)
            self.logger.debug("HTML> {}".format(html))
            code = match1(html, '<code>([^<])')
            if code:
                continue
            urls, size, fmt = parse_cid_playurl(html)
            if fmt == 'hdmp4':
                ext = 'mp4'
            elif fmt == 'flv720':
                ext = 'flv'
            elif fmt == 'flv480':
                ext = 'flv'
            else:
                ext = fmt
            prf = self.fmt_2_profile[fmt]
            st = self.profile_2_type[prf]
            if st in info.stream_types:
               continue
            info.stream_types.append(st)
            info.streams[st] = {'container': ext, 'video_profile': prf, 'src' : urls, 'size': size}
            assert len(info.stream_types), "can't play this video!!"
        return info
