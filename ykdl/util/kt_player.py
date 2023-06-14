'''Parse & decrypto license code for KVS Player.'''
# https://www.kernel-scripts.com/en/documentation/player/

from .match import *
from ..mediainfo import MediaStreams

import time


__all__ = ['get_kt_playlist', 'get_kt_media']

profile_2_id = {
    '2160P': '2K',
    '1080P': 'BD',
     '720P': 'TD',
     '480P': 'HD',
     '360P': 'SD'
}

def get_license(html):
    license = match1(html, '''license_code: ['"]\$(\d{15})['"]''')
    if license is None:
        return
    mod = license.replace('0', '1')
    mod = str(4 * abs(int(mod[:8]) - int(mod[-8:])))
    nlicense = []
    plicense = []
    for o in range(8):
        for i in range(4):
            nlicense.append((int(license[o + i]) + int(mod[o])) % 10)
    n = sum(nlicense)
    for i, l in enumerate(nlicense):
        plicense.append((i, (n + i) % 32))
        n -= l
    plicense.reverse()
    return plicense

def decrypto(url, license):
    l1 = match1(url, '/([\da-f]{42})/')
    l2 = list(l1)
    for i, l in license:
        l2[i], l2[l] = l2[l], l2[i]
    l2 = ''.join(l2)
    return url.replace(l1, l2)

def get_urls(html):
    rnd = int((time.time() - 10) * 1e3)
    license = get_license(html)
    if license is None:
        return
    for url in matchall(html, '''function/0/(http[^'"]+)'''):
        url = decrypto(url, license)
        if '?' in url:
            yield f'{url}&rnd={rnd}'
        else:
            yield f'{url}?rnd={rnd}'

def get_kt_playlist(html):
    streams = MediaStreams()
    for url in get_urls(html):
        stream_profile = (match1(url, '_(\d+)p?.mp4') or '480') + 'P'
        stream = profile_2_id[stream_profile]
        streams[stream] = {
            'container': 'mp4',
            'profile': stream_profile,
            'src': [url]
        }
    return streams

def get_kt_media(html):
    return get_kt_playlist(html)[0]['src']
