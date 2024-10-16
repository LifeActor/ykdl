# -*- coding: utf-8 -*-

from ._common import *
from .singlemultimedia import contentTypes


# TODO: subtitles support
# REF: https://developer.mozilla.org/zh-CN/docs/Web/API/WebVTT_API

pattern_ext = r'''(?ix)
["'](
    (?:https?:|\\?/)[^"'#]+?\.
    (
        m3u8?                       | # HLS
        mpd                         | # DASH
        mp4|webm                    | # video/audio
        f4v|flv|ts                  | # video
        mov|qt|m4[pv]|og[mv]        | # video
        ogg|vid|3gp|mpe?g           | # video/audio
        mp3|flac|wave?|oga|aac|weba   # audio
    )
    /?(?:[\?&].+?)?
)["'#]
'''
pattern_src = r'''(?ix)
<(?:video|audio|source)[^>]+?
src=["']?((?:https?:|\\?/)[^"' ]+)["' ]
[^>]*?
(?:
    type=["']((?:video|audio|application)/[^"']+)["']
    |
    [^>](?!type)*>
)
'''

class GeneralSimple(Extractor):
    name = 'GeneralSimple (通用简单)'

    def list_only(self):
        return True

    def prepare_list(self):
        html = get_content(self.url)
        title = match1(html, '<meta property="og:title" content="([^"]+)',
                             '''video_title\s*[:=]\s*['"](.+?)['"],''',
                             '<title>(.+?)</title>')
        _title, domain = matchm(title, '(.+) [-|*] (.+)$')
        if domain and domain.lower() in self.url.split('/')[2]:
            title = _title

        streams = get_kt_playlist(html)
        if streams:
            info = MediaInfo(self.name)
            info.title = title
            info.streams = streams
            info.extra.referer = self.url
            yield info
            return

        for i in range(2):
            urls = matchall(html, pattern_src)
            if urls:
                urls = [(i and url or unescape(url), ctype, None) for url, ctype in urls]
                break
            urls = matchall(html, pattern_ext)
            if urls:
                urls = [(i and url or unescape(url), None, ext) for url, ext in urls]
                break
            if i == 0:
                html = unquote(unescape(html))

        urls = set(urls)
        self.set_index(0, len(urls))
        for i, (url, ctype, ext) in enumerate(urls):
            info = MediaInfo(self.name)
            info.title = len(urls) == 1 and title or f'{title}_{i+1}'
            url = literalize(url, True)
            url = match1(url, '.+(https?://.+)') or url  # redirect clear
            if url[:2] == '//':
                url = self.url[:self.url.find('/')] + url
            elif url[0] == '/':
                url = self.url[:self.url.find('/', 9)] + url
            if '?' not in url and '&' in url:
                url = url.replace('&', '?', 1)
            if ext is None or ctype:
                ctype = str(ctype).lower()
                ext = contentTypes.get(ctype) or url_info(url)[1] or (
                            ctype.startswith('audio') and 'mp3' or 'mp4')
            if ext[:3] == 'm3u':
                info.streams = load_m3u8_playlist(url, headers={'Referer': self.url})
            else:
                info.streams['current'] = {
                    'container': ext,
                    'profile': 'current',
                    'src': [url],
                    'size': 0
                }
            info.extra.referer = self.url
            yield info

site = GeneralSimple()
