#!/usr/bin/env python

from ..common import *
from xml.dom.minidom import parseString

from ..extractor import VideoExtractor

class Tudou(VideoExtractor):
    name = "土豆 (tudou)"

    def prepare(self, **kwargs):
        assert self.url or self.vid
        html = ''
        if self.url:
            html = get_content(self.url)
            self.title = match1(html, '<title>([^<]+)')
            vcode = match1(html, 'vcode\s*[:=]\s*\'([^\']+)\'')
            if vcode:
                from .youku import site as youku
                youku.download_by_vid(vcode, **kwargs)
                exit(0)
            else:
                self.vid = match1(html, 'iid\s*[:=]\s*(\d+)')
        else:
            if 'title' in kwargs and kwargs['title']:
                self.title = kwargs['title']
            else:
                self.title = self.name + self.vid

        data = json.loads(get_content('http://www.tudou.com/outplay/goto/getItemSegs.action?iid=%s' % self.vid))

        temp = max([data[i] for i in data if 'size' in data[i][0]], key=lambda x:sum([part['size'] for part in x]))
        vids, size = [t["k"] for t in temp], sum([t["size"] for t in temp])
        urls = [[n.firstChild.nodeValue.strip()
             for n in
                parseString(
                    get_content('http://ct.v2.tudou.com/f?id=%s' % vid))
                .getElementsByTagName('f')][0]
            for vid in vids]
        ext = r1(r'http://[\w.]*/(\w+)/[\w.]*', urls[0])
        self.stream_types.append('current')
        self.streams['current'] = {'container': ext, 'video_profile': 'current', 'src' : urls, 'size': size}

    def parse_plist(self):
        html = get_content(self.url)
        lcode = r1(r"lcode:\s*'([^']+)'", html)
        plist_info = json.loads(get_content('http://www.tudou.com/crp/plist.action?lcode=' + lcode))
        return ([(item['kw'], item['iid']) for item in plist_info['items']])

    def download_playlist_by_url(self, url, **kwargs):
        self.url = url
        videos = self.parse_plist()
        for i, (title, id) in enumerate(videos):
            print('Processing %s of %s videos...' % (i + 1, len(videos)))
            self.download_by_vid(id, title=title, **kwargs)

site = Tudou()
download = site.download_by_url
download_playlist = site.download_playlist_by_url
