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

    def prepare_mid(self):
        return match1(self.url, '\D(\d{4}:(?:\d{16}|\w{32}))(?:\W|$)',
                                'media_id=(\d{16})')

    def prepare(self):
        if 'passport.weibo' in self.url:
            url = parse_qs(self.url.split('?', 1)[-1]).get('url')
            assert url, 'lost the url param in a link of "passport.weibo"'
            self.url = url[0]

        info = MediaInfo(self.name)
        add_header('User-Agent', 'Baiduspider')

        def append_stream(stream_profile, stream_quality, url):
            stream_id = self.quality_2_id[stream_quality]
            info.streams[stream_id] = {
                'container': 'mp4',
                'profile': stream_profile,
                'src': [url]
            }

        try:
            self.mid
        except AssertionError:
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
                    stream_quality = stream['quality_label'].upper()
                    stream_profile = stream['quality_desc'] + ' ' + stream_quality
                    stream_quality = match1(stream_quality, '(\d+)')
                    append_stream(stream_profile, stream_quality, stream['url'])
            else:
                url = match1(html, 'action-data="[^"]+?&video_src=([^"&]+)')
                if url:
                    info.streams['current'] = {
                        'container': 'mp4',
                        'profile': 'current',
                        'src': [unquote(url)]
                    }
            if info.streams:
                info.title = match1(html, '<meta content="([^"]+)" name="description"').split('\n')[0]
                info.artist = match1(html, '<meta content="([^"]+)" name="keywords"').split(',')[0]
                i = info.title.find('】') + 1
                if i:
                    info.title = info.title[:i]
                return info
            else:
                self.mid = match1(html, 'objectid=(\d{4}:(?:\d{16}|\w{32}))\W')

        if ':' not in self.mid:
            self.mid = '1034:' + self.mid  # oid, the prefix is not necessary and would not be checked
        vdata = get_response('https://weibo.com/tv/api/component',
                    headers={
                        'Referer': 'https://weibo.com/tv/show/' + self.mid
                    },
                    data={
                        'data': json.dumps({
                            'Component_Play_Playinfo': {'oid': self.mid}
                        })
                    }).json()['data']['Component_Play_Playinfo']

        info.title = vdata['title']
        info.artist = vdata['author']
        for stream_profile, url in vdata['urls'].items():
            if url:
                stream_quality = match1(stream_profile, '(\d+)')
                append_stream(stream_profile, stream_quality, 'https:' + url)

        return info

site = Weibo()
