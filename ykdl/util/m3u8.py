from logging import getLogger

from ..mediainfo import MediaStreams
from .http import get_response
from .human import format_vps

logger = getLogger(__name__)


__all__ = ['live_m3u8', 'crypto_m3u8', 'load_m3u8_playlist', 'load_m3u8']

def no_m3u8_warning():
    logger.warning('No python-m3u8 found, use stub m3u8!!! '
                   'Please install it by `pip install m3u8`')

def live_error():
    raise NotImplementedError(
            'Internal live m3u8 parser and downloader had not '
            'be implementated! Please use FFmpeg instead.')

def load_live_m3u8(url):
    live_error()

def live_m3u8_lenth():
    live_error()

try:
    import m3u8

except:
    raise
    def live_m3u8(url):
        no_m3u8_warning()
        return None

    def crypto_m3u8(url):
        no_m3u8_warning()
        return None

    def load_m3u8_playlist(url):
        no_m3u8_warning()
        streams = MediaStreams()
        streams['current'] = {
            'container': 'm3u8',
            'video_profile': 'current',
            'src' : [url],
            'size': 0
        }
        return streams

    def load_m3u8(url):
        no_m3u8_warning()
        return [url], [], []

else:
    import urllib.parse
    from functools import lru_cache

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
    @lru_cache(maxsize=None)  # live is disabled, results can be cached safely
    def _download(uri, headers):
        response = get_response(uri, dict(headers))
        return response.text, _parsed_url(response.url)

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

    def crypto_m3u8(url):
        m = _load(url)
        return any(m.keys + m.session_keys)  # ignore method NONE

    def _get_stream_info(l, name):
        return getattr(getattr(l, 'stream_info',
                               getattr(l, 'iframe_stream_info', None)),
                       name)

    def load_m3u8_playlist(url):

        def append_stream(stype, profile, urls):
            streams[stype] = {
                'container': 'm3u8',
                'video_profile': profile,
                'src' : urls,
                'size': 0
            }

        streams = MediaStreams()
        m = _load(url)
        ll = m.playlists or m.iframe_playlists
        if ll:
            for l in ll:
                resolution = _get_stream_info(l, 'resolution')
                if resolution:
                    append_stream(*format_vps(*resolution), [l.absolute_uri])
                else:
                    bandwidth = str(_get_stream_info(l, 'bandwidth'))
                    append_stream(bandwidth, bandwidth, [l.absolute_uri])
        else:
            append_stream('current','current', [url])
        return streams

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
