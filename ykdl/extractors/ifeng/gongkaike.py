# -*- coding: utf-8 -*-

from .._common import *
from .news import Ifeng


class IfengOpenC(Ifeng):
    name = '凤凰公开课 (ifeng open course)'  # 404

    def prepare(self):
        info = MediaInfo(self.name)

        xml = get_content(
                'http://vxml.ifengimg.com/video_info_new/{}/{}/{}.xml'
                .format(self.mid[-2], self.mid[-2:], self.mid))

        info.title = match1(xml, 'SE_Title="([^"]+)')
        urls = matchall(xml, 'playurl="([^"]+)')
        urls = ['http://ips.ifeng.com/' + u[7:] for u in urls ]
        info.streams['current'] = {
            'container': 'mp4',
            'profile': 'current',
            'src': urls
        }

        return info

site = IfengOpenC()
