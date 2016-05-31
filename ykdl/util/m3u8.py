#!/usr/bin/env python

try:

    import m3u8

    def load_m3u8_playlist(url):
        stream_types = []
        streams = {}
        m = m3u8.load(url).playlists
        for l in m:
            stream_types.append(l.stream_info.bandwidth)
            streams[l.stream_info.bandwidth] = {'container': 'm3u8', 'video_profile': l.stream_info.bandwidth, 'src' : [l.absolute_uri], 'size': 0}
        stream_types.sort()
        return stream_types, streams

    def load_m3u8(url):
        urls = []
        m =  m3u8.load(url)
        for seg in m.segments:
            urls.append(seg.absolute_uri)
        return urls

except:
    def load_m3u8_playlist(url):
        stream_types = ['current']
        streams['current'] = {'container': 'm3u8', 'video_profile': 'current', 'src' : [url], 'size': 0}

    def load_m3u8(url):
        return [url]

