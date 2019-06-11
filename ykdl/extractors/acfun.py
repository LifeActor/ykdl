#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.html import get_content, add_header
from ..util.match import match1, matchall
from ..embedextractor import EmbedExtractor
from ..videoinfo import VideoInfo
from ..compact import urlencode

import json
import time

class Acfun(EmbedExtractor):

    name = u'ACfun 弹幕视频网'

    def build_videoinfo(self, title, artist, size, urls):
        info = VideoInfo(self.name)
        info.title = title
        info.artist = artist
        info.stream_types.append('current')
        info.streams['current'] = {
            'container': 'm3u8',
            'src': urls,
            'size' : size
        }
        self.video_info['info'] = info

    def prepare(self):
        add_header('Referer', 'https://www.acfun.cn/')
        html = get_content(self.url)
        pageInfo = json.loads(match1(html, u'var (?:pageInfo|bgmInfo) = ({.+?})</script>'))
        bgmInfo = pageInfo
        title = pageInfo.get('title')
        if title:
            # user up
            artist = pageInfo['username']
            sourceVid = pageInfo['videoId']
            sub_title = ''
        else:
            # bangumi
            title = pageInfo['album']['title']
            artist = None
            videoInfo = pageInfo['video']['videos'][0]
            sourceVid = videoInfo['videoId']
            sub_title = u'{} {}'.format(videoInfo['episodeName'], videoInfo['newTitle']).rstrip()

        try:
            data = json.loads(get_content('https://www.acfun.cn/video/getVideo.aspx?id={}'.format(sourceVid)))
        except:
            # TODO: get more qualities
            data = json.loads(get_content('https://www.acfun.cn/rest/pc-direct/play/playInfo/m3u8Auto?videoId={}'.format(sourceVid)))
            stream = data['playInfo']['streams'][0]
            size = stream['size']
            urls = stream['playUrls']
            title = u'{} - {}'.format(title, sub_title)
            self.build_videoinfo(title, artist, size, urls)
            return

        sourceType = data['sourceType']
        sourceId = data['sourceId']
        sub_title = sub_title or data['title']
        if sub_title != 'Part1' or len(pageInfo.get('videoList', sub_title)) > 1:
            title = u'{} - {}'.format(title, sub_title)

        if sourceType == 'zhuzhan':
            sourceType = 'acorig'
            encode = data['encode']
            sourceId = (sourceId, encode)
        elif sourceType == 'letv':
            #workaround for letv, because it is letvcloud
            sourceType = 'le.letvcloud'
            sourceId = (sourceId, '2d8c027396')
        elif sourceType == 'qq':
            sourceType = 'qq.video'

        self.video_info['site'] = sourceType
        self.video_info['vid'] = sourceId
        self.video_info['title'] = title
        self.video_info['artist'] = artist

    def prepare_playlist(self):
        html = get_content(self.url)
        if 'bangumi' in self.url:
            albumId = match1(self.url, '/a[ab](\d+)')
            groupId = match1(html, '"groups":[{[^}]*?"id":(\d+)')
            params = {
                'albumId': albumId,
                'groupId': groupId,
                'num': 1,
                'size': 20,
                '_': int(time.time() * 1000),
            }
            data = json.loads(get_content('https://www.acfun.cn/album/abm/bangumis/video?' + urlencode(params)))
            videos = []
            for c in data['data']['content']:
                vid = c['videos'][0]['id']
                v = '/bangumi/ab{}_{}_{}'.format(albumId, groupId, vid)
                videos.append(v)
        else:
            videos = matchall(html, ['href="(/v/[a-zA-Z0-9_]+)" title="'])

        for v in videos:
            next_url = 'https://www.acfun.cn' + v
            video_info = self.new_video_info()
            video_info['url'] = next_url
            self.video_info_list.append(video_info)

site = Acfun()
