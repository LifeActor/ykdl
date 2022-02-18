# -*- coding: utf-8 -*-

from ._common import *


class Weibo(Extractor):
    name = '微博 (Weibo)'

    quality_2_id = {
           '4': '4K',
           '2': '2K',
        '1080': 'BD',
         '720': 'TD',
         '480': 'HD',
         '360': 'SD'
    }

    def prepare(self):
        if 'passport.weibo' in self.url:
            url = parse_qs(self.url.split('?', 1)[-1]).get('url')
            assert url, 'lost the url param in a link of "passport.weibo"'
            self.url = url[0]

        info = MediaInfo(self.name)

        add_header('User-Agent', 'Baiduspider')

        self.vid = match1(self.url, '\D(\d{4}:(?:\d{16}|\w{32}))(?:\W|$)',
                                    'media_id=(\d{16})')

        def append_stream(video_profile, video_quality, url):
            stream_id = self.quality_2_id[video_quality]
            info.streams[stream_id] = {
                'video_profile': video_profile,
                'container': 'mp4',
                'src' : [url]
            }

        if self.vid is None:
            rurl = get_location(self.url)
            assert '/sorry?' not in rurl, 'can not find any video!!!'
            page = match1(rurl, 'https?://[^/]+(/\d+/\w+)')
            if page is None or match1(page, '/(\d+)$'):
                html = get_content(rurl.replace('//weibo.', '//hk.weibo.')
                                       .replace('/user/', '/'))
                page = match1(html, '"og:url".+weibo.com(/\d+/\w+)')
            assert page, 'can not find any video!!!'
            html = get_content('https://weibo.com' + page)
            streams = match1(html, 'quality_label_list=([^"]+)').split('&')[0]
            if streams:
                streams = json.loads(unquote(streams))
                for stream in streams:
                    video_quality = stream['quality_label'].upper()
                    video_profile = stream['quality_desc'] + ' ' + video_quality
                    video_quality = match1(video_quality, '(\d+)')
                    append_stream(video_profile, video_quality, stream['url'])
            else:
                url = match1(html, 'action-data="[^"]+?&video_src=([^"&]+)')
                if url:
                    info.streams['current'] = {
                        'video_profile': 'current',
                        'container': 'mp4',
                        'src' : [unquote(url)]
                    }
            if info.streams:
                info.title = match1(html, '<meta content="([^"]+)" name="description"').split('\n')[0]
                info.artist = match1(html, '<meta content="([^"]+)" name="keywords"').split(',')[0]
                i = info.title.find('】') + 1
                if i:
                    info.title = info.title[:i]
            else:
                self.vid = match1(html, 'objectid=(\d{4}:(?:\d{16}|\w{32}))\W')
                assert self.vid, 'can not find any video!!!'

        if self.vid:
            if ':' not in self.vid:
                self.vid = '1034:' + self.vid  # oid, the prefix is not necessary and would not be checked
            vdata = get_response('https://weibo.com/tv/api/component',
                        headers={
                            'Referer': 'https://weibo.com/tv/show/' + self.vid
                        },
                        data={
                            'data': json.dumps({
                                'Component_Play_Playinfo': {'oid': self.vid}
                            })
                        }).json()['data']['Component_Play_Playinfo']

            info.title = vdata['title']
            info.artist = vdata['author']
            for video_profile, url in vdata['urls'].items():
                if url:
                    video_quality = match1(video_profile, '(\d+)')
                    append_stream(video_profile, video_quality, 'https:' + url)

        return info

site = Weibo()
