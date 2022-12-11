# -*- coding: utf-8 -*-

from ._common import *
from . import _byted


class IXiGua(Extractor):
    name = '西瓜视频 (IXiGua)'

    @staticmethod
    def profile_2_id(profile):
        if profile[-1] == 'p':
            return {
               '1080p': 'BD',
                '720p': 'TD',
                '480p': 'HD',
                '360p': 'SD',
             }[profile]
        if profile[-1] == 'k':
            return profile.upper()
        assert 0, 'unsupported profile: %r' % profile

    def prepare(self):
        info = MediaInfo(self.name)

        html = _byted.get_content(self.url)
        data = match1(html, 'window._SSR_HYDRATED_DATA=(.+?)</script>')
        self.logger.debug('data: \n%s', data)
        data = json.loads(data.replace('undefined', 'null'))

        video_info = data['anyVideo']['gidInformation']['packerData']

        if 'video' in video_info:
            video_info = video_info['video']
            info.title = video_info['title']
            info.artist = video_info['user_info']['name']
        else:
            albumInfo = video_info['albumInfo']
            al_title = albumInfo['title']
            info.artist = albumInfo['userInfo']['name']
            for c in (*albumInfo['areaList'],
                       albumInfo['year'],
                      *albumInfo['tagList'],
                      *[a['name'] for a in albumInfo.get('actorList', [])]):
                info.add_comment(c)
            ep_title = video_info['episodeInfo']['title']
            if al_title in ep_title:
                info.title = ep_title
            else:
                info.title = '{al_title} - {ep_title}'.format(**vars())

        videoResource = video_info['videoResource']['normal']
        info.duration = videoResource['video_duration']

        for v in videoResource['video_list'].values():
            stream_profile = v['definition']
            stream_id = self.profile_2_id(stream_profile)
            info.streams[stream_id] = {
                'container': v['vtype'],
                'profile': stream_profile,
                'src' : [unb64(v['backup_url_1'])],  # main_url status 403
                'size': v['size']
            }

        return info

    def prepare_list(self):
        albumId, episodeId = matchall(self.url, '.ixigua.com/(\d+)(?:.+?id=(\d+))?')[0]
        data = get_response('https://www.ixigua.com/api/albumv2/details',
                            headers={'Referer': 'https://www.ixigua.com/'},
                            params={'albumId': albumId}).json()
        assert data['code'] == 200, "can't fetch playlist!"

        ep_ids = [b for a, b in sorted((ep['seq'], ep['episodeId'])
                                       for ep in data['data']['playlist'])]
        self.set_index(episodeId, ep_ids)
        for ep_id in ep_ids:
            yield 'https://www.ixigua.com/{albumId}?id={ep_id}'.format(**vars())

site = IXiGua()
