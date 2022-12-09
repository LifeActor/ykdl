# -*- coding: utf-8 -*-

from .._common import *


class HuajiaoVideo(Extractor):
    name = 'huajiao video (花椒小视频)'

    def get_data(self, type):
        html = get_content(self.url)
        data = match1(html, '_DATA.{type} = (.+?[}}\]]);'.format(**vars()))
        self.logger.debug('%s data:\n%s', type, data)
        return json.loads(data)

    def generate_info(self, data):
        info = MediaInfo(self.name)
        info.artist = data['user_name']
        info.title = data['video_name']
        info.duration = data.get('duration')
        info.streams['current'] = {
            'container': 'mp4',
            'profile': 'current',
            'src': [data['video_url']]
        }
        return info

    def prepare_feed(self):
        data = self.get_data('feed')
        feed = data['feed']
        feed['user_name'] = data['author']['nickname']
        return feed

    def prepare(self):
        return self.generate_info(self.prepare_feed())

    def prepare_list(self):
        info = self.prepare_feed()
        infos = self.get_data('list')

        vid = info['vid']
        vids = [i['vid'] for i in infos]
        if vid not in vids:
            vids.insert(0, vid)
            infos.insert(0, info)
        self.set_index(vid, vids)

        for info in infos:
            yield self.generate_info(info)

site = HuajiaoVideo()
