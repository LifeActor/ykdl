from logging import getLogger

from ..mediainfo import MediaStreams
from .http import get_response
from .human import format_vps

logger = getLogger(__name__)


__all__ = ['live_m3u8', 'crypto_m3u8', 'load_m3u8_playlist', 'load_m3u8']


def live_error():
    raise NotImplementedError(
            'Internal live m3u8 parser and downloader had not '
            'be implementated! Please use FFmpeg instead.')

def load_live_m3u8(url):
    live_error()

def live_m3u8_lenth():
    live_error()

import m3u8
from urllib.parse import urljoin

class HTTPClient():
    hkwargs = {}
    def download(self, uri, timeout=None, headers={}, *args, **kwargs):
        # live is disabled, results can be cached safely
        response = get_response(uri, headers, cache=True, **self.hkwargs)
        return response.text, urljoin(response.url, '.')

def _load(uri, **kwargs):
    '''Support keyword arguments from m3u8.load().
    Argument "hkwargs" pass on a keyword arguments dict to .http.get_response().
    '''
    http_client = kwargs.get('http_client') or HTTPClient
    hkwargs = kwargs.pop('hkwargs', None)
    if isinstance(http_client, type):
        http_client = http_client()
    if isinstance(http_client, HTTPClient) and hkwargs:
        headers = hkwargs.pop('headers', None)
        if headers:
            if 'headers' in kwargs:
                kwargs['headers'].update(headers)
            else:
                kwargs['headers'] = headers
        http_client.hkwargs = hkwargs
    kwargs['http_client'] = http_client
    return m3u8.load(uri, **kwargs)

def live_m3u8(url, **kwargs):
    '''Params: as same as _load().'''
    m = _load(url, **kwargs)
    ll = m.playlists or m.iframe_playlists
    if ll:
        m = _load(ll[0].absolute_uri, **kwargs)
    return not (m.is_endlist or m.playlist_type == 'VOD')

def crypto_m3u8(url, **kwargs):
    '''Params: as same as _load().'''
    m = _load(url, **kwargs)
    for k in m.keys:
        try:
            assert not k.uri.startswith('skd:'), 'Unsupported FairPlay Streaming'
        except AttributeError:
            pass
    return any(m.keys + m.session_keys)  # ignore method NONE

def _get_stream_info(l, name):
    return getattr(getattr(l, 'stream_info',
                           getattr(l, 'iframe_stream_info', None)),
                   name)

def load_m3u8_playlist(url, **kwargs):
    '''Params: as same as _load().'''

    def append_stream(stream_id, stream_profile, urls):
        streams[stream_id] = {
            'container': 'm3u8',
            'profile': stream_profile,
            'src': urls
        }

    streams = MediaStreams()
    m = _load(url, **kwargs)
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

def load_m3u8(url, **kwargs):
    '''Params: as same as _load().'''

    def load_media(l=None, m=None):
        urls = []
        if l:
            m = _load(l.absolute_uri, **kwargs)
        if m:
            for seg in m.segments:
                urls.append(seg.absolute_uri)
        return urls

    if live_m3u8(url, **kwargs):
        live_error()
    m = _load(url, **kwargs)
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
