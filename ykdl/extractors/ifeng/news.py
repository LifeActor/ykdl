# -*- coding: utf-8 -*-

from .._common import *


class Ifeng(Extractor):
    name = '凤凰新闻 (ifeng news)'  # EXPIRED

    types_2_id_profile = {
          '1M': ['TD', '超清'],
        '500k': ['HD', '高清'],
        '350k': ['SD', '标清']
    }

    def prepare(self):
        info = MediaInfo(self.name)
        if not self.vid:
            self.vid= match1(self.url, '#([a-zA-Z0-9\-]+)',
                                       '/([a-zA-Z0-9\-]+).shtml')
        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, '"vid": "([^"]+)',
                                    'vid: "([^"]+)')
        assert self.vid, 'No VID found!!'

        doc = get_response(
                'http://vxml.ifengimg.com/video_info_new/{}/{}/{}.xml'
                .format(self.vid[-2], self.vid[-2:], self.vid)).xml()
        info.title = doc.getElementsByTagName('item')[0].getAttribute('Name')
        videos = doc.getElementsByTagName('videos')
        for v in videos[0].getElementsByTagName('video'):
            ext = v.getAttribute('mediaType')
            _t = v.getAttribute('type')
            _u = v.getAttribute('VideoPlayUrl')
            stream, profile = self.types_2_id_profile[_t]
            info.streams[stream] = {
                'container': ext,
                'video_profile': profile,
                'src' : [_u],
                'size': 0
                }

        return info

site = Ifeng()
