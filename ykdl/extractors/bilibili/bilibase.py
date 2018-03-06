#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from ykdl.util.html import get_content, add_header, fake_headers, get_location
from ykdl.util.match import match1, matchall
from xml.dom.minidom import parseString


def parse_cid_playurl(xml):
    urls = []
    size = 0
    doc = parseString(xml.encode('utf-8'))
    ext = doc.getElementsByTagName('format')[0].firstChild.nodeValue
    qlt = doc.getElementsByTagName('quality')[0].firstChild.nodeValue
    aqlts = doc.getElementsByTagName('accept_quality')[0].firstChild.nodeValue.split(',')
    for durl in doc.getElementsByTagName('durl'):
        urls.append(durl.getElementsByTagName('url')[0].firstChild.nodeValue)
        size += int(durl.getElementsByTagName('size')[0].firstChild.nodeValue)
    return urls, size, ext, qlt, aqlts

class BiliBase(VideoExtractor):
    #supported_stream_profile = [u'蓝光', u'超清', u'高清', u'流畅']
    profile_2_type = {u'蓝光': 'BD', u'超清': 'TD', u'高清': 'HD', u'流畅' :'SD'}
    qlt_2_profile = {'80': u'蓝光', '64': u'超清',  '48': u'高清',  '32': u'高清', '16': u'流畅'}

    def prepare(self):
        info = VideoInfo(self.name)
        add_header("Referer", "https://www.bilibili.com/")
        info.extra["referer"] = "https://www.bilibili.com/"
        info.extra["ua"] = fake_headers['User-Agent']

        self.vid, info.title = self.get_vid_title()

        assert self.vid, "can't play this video: {}".format(self.url)

        def get_video_info(qn=0):
            api_url = self.get_api_url(qn)
            html = get_content(api_url)
            self.logger.debug("HTML> {}".format(html))
            code = match1(html, '<code>([^<])')
            if code:
                return
            urls, size, fmt, qlt, aqlts = parse_cid_playurl(html)
            if 'mp4' in fmt:
                ext = 'mp4'
            elif 'flv' in fmt:
                ext = 'flv'

            prf = self.qlt_2_profile[qlt]
            st = self.profile_2_type[prf]
            if st not in info.streams:
                info.stream_types.append(st)
                info.streams[st] = {'container': ext, 'video_profile': prf, 'src' : urls, 'size': size}

            if qn == 0:
                aqlts.remove(qlt)
                for aqlt in aqlts:
                    get_video_info(aqlt)

        get_video_info()

        assert len(info.stream_types), "can't play this video!!"
        return info
