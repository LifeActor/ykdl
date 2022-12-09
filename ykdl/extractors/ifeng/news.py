# -*- coding: utf-8 -*-

from .._common import *


class Ifeng(Extractor):
    name = '凤凰新闻 (ifeng news)'  # EXPIRED

    types_2_id_profile = {
          '1M': ['TD', '超清'],
        '500k': ['HD', '高清'],
        '350k': ['SD', '标清']
    }

    def prepare_mid(self):
        mid = match1(self.url, '#([a-zA-Z0-9\-]+)',
                               '/([a-zA-Z0-9\-]+).shtml')
        if mid is None:
            html = get_content(self.url)
            mid = match1(html, r'\bvid"?: "([^"]+)')
        return mid

    def prepare(self):
        info = MediaInfo(self.name)

        doc = get_response(
                'http://vxml.ifengimg.com/video_info_new/{}/{}/{}.xml'
                .format(self.mid[-2], self.mid[-2:], self.mid)).xml()
        info.title = doc.getElementsByTagName('item')[0].getAttribute('Name')
        videos = doc.getElementsByTagName('videos')
        for v in videos[0].getElementsByTagName('video'):
            ext = v.getAttribute('mediaType')
            _t = v.getAttribute('type')
            _u = v.getAttribute('VideoPlayUrl')
            stream_id, stream_profile = self.types_2_id_profile[_t]
            info.streams[stream_id] = {
                'container': ext,
                'profile': stream_profile,
                'src': [_u]
                }

        return info

site = Ifeng()
