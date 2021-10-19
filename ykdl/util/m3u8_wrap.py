#!/usr/bin/env python

from logging import getLogger
from .html import get_content_and_location

logger = getLogger("m3u8_wrap")


def no_m3u8_warning():
    logger.warning('No python-m3u8 found, use stub m3u8!!! '
                   'please install it by pip install m3u8')

def live_error():
    raise NotImplementedError('Internal live m3u8 parser and downloader '
                              'had not be implementated!')

def load_live_m3u8(url):
    live_error()

def live_m3u8_lenth():
    live_error()

try:
    import m3u8

except:
    def live_m3u8(url):
        no_m3u8_warning()
        return None

    def load_m3u8_playlist(url):
        no_m3u8_warning()
        stream_types = ['current']
        streams['current'] = {
            'container': 'm3u8',
            'video_profile': 'current',
            'src' : [url],
            'size': 0
        }
        return stream_types, streams

    def load_m3u8(url):
        no_m3u8_warning()
        return [url], [], []

else:
    import urllib.parse
    from functools import cache

    # patch urljoin to allow '//'
    def urljoin(base, url, *args, **kwargs):
        base = base.replace('://', '\1')
        url = url.replace('://', '\1')
        while '//' in base:
            base = base.replace('//', '/\0/')
        while '//' in url:
            url = url.replace('//', '/\0/')
        return _urljoin(base.replace('\1', '://'), url.replace('\1', '://'),
                        *args, **kwargs).replace('\0', '')

    def _parsed_url(url):
         return urljoin(url, '.')

    _urljoin = urllib.parse.urljoin
    urllib.parse.urljoin = urljoin
    m3u8._parsed_url = _parsed_url

    # hack into HTTP request of m3u8, let it use cykdl's settings
    @cache
    def _download(uri, headers):
        # live is disabled, results can be cached safely
        kwargs = {}
        headers = dict(headers)
        headers.pop('Accept-Encoding', None)
        if headers:
            kwargs['headers'] = headers
        content, uri = get_content_and_location(uri, **kwargs)
        base_uri = _parsed_url(uri)
        return content, base_uri

    try:
        import m3u8.httpclient
    except ImportError:
        def _load_from_uri(uri, timeout=None, headers={},
                            custom_tags_parser=None, verify_ssl=True):
            content, base_uri = _download(uri, tuple(headers.items()))
            return m3u8.M3U8(content, base_uri=base_uri,
                             custom_tags_parser=custom_tags_parser)

        m3u8._load_from_uri = _load_from_uri
        _load = m3u8.load
    else:
        class HTTPClient():
            def download(self, uri, timeout=None, headers={}, *args, **kwargs):
                return _download(uri, tuple(headers.items()))

        def _load(uri, timeout=None, headers={}, custom_tags_parser=None,
                  http_client=HTTPClient(), *args, **kwargs):
            return m3u8.load(uri, headers=headers,
                                  custom_tags_parser=custom_tags_parser,
                                  http_client=http_client)

    def live_m3u8(url):
        m = _load(url)
        ll = m.playlists or m.iframe_playlists
        if ll:
            m = _load(ll[0].absolute_uri)
        return not (m.is_endlist or m.playlist_type == 'VOD')

    def _get_stream_info(l, name):
        return getattr(getattr(l, 'stream_info',
                               getattr(l, 'iframe_stream_info', None)),
                       name)

    def load_m3u8_playlist(url):

        def append_stream(stype, urls):
            stream_types.append(stype)
            streams[stype] = {
                'container': 'm3u8',
                'video_profile': stype,
                'src' : urls,
                'size': 0
            }

        stream_types = []
        streams = {}
        m = _load(url)
        ll = m.playlists or m.iframe_playlists
        if ll:
            for l in ll:
                bandwidth = str(_get_stream_info(l, 'bandwidth'))
                append_stream(bandwidth, [l.absolute_uri])
            stream_types.sort(key=lambda i: int(i), reverse=True)
        else:
            append_stream('current', [url])
        return stream_types, streams

    def load_m3u8(url):

        def load_media(l=None, m=None):
            urls = []
            if l:
                m = _load(l.absolute_uri)
            if m:
                for seg in m.segments:
                    urls.append(seg.absolute_uri)
            return urls

        if live_m3u8(url):
            live_error()
        m = _load(url)
        ll = m.playlists or m.iframe_playlists
        if ll:
            ll.sort(key=lambda l: _get_stream_info(l, 'bandwidth'))
            l = ll[-1]
            media = {e.type: e for e in getattr(l, 'media', [])}
            urls = load_media(l=l)
        else:
            media = {}
            urls = load_media(m=m)
        audio = load_media(media.get('AUDIO'))
        subtitle = load_media(media.get('SUBTITLES'))
        if audio and urls[0] == audio[0]:
            audio.clear()
        return urls, audio, subtitle
