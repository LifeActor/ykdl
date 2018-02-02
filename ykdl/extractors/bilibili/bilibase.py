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
    supported_stream_profile = [u'超清', u'高清', u'流畅']
    profile_2_type = {u'超清': 'TD', u'高清': 'HD', u'流畅' :'SD'}

    def prepare(self):
        info = VideoInfo(self.name)
        add_header("Referer", "http://www.bilibili.com")
        info.extra["referer"] = "http://www.bilibili.com"
        info.extra["ua"] = fake_headers['User-Agent']

        self.vid, info.title = self.get_vid_title()

        assert self.vid, "can't play this video: {}".format(self.url)

        for q in self.supported_stream_profile:
            api_url = self.get_api_url(3-self.supported_stream_profile.index(q))
            html = get_content(api_url)
            self.logger.debug("HTML> {}".format(html))
            code = match1(html, '<code>([^<])')
            if code:
                continue
            urls, size, ext = parse_cid_playurl(html)
            if ext == 'hdmp4':
                ext = 'mp4'

            info.stream_types.append(self.profile_2_type[q])
            info.streams[self.profile_2_type[q]] = {'container': ext, 'video_profile': q, 'src' : urls, 'size': size}
            assert len(info.stream_types), "can't play this video!!"
        return info
