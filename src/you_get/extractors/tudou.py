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

        data = json.loads(get_decoded_html('http://www.tudou.com/outplay/goto/getItemSegs.action?iid=%s' % self.vid))

        temp = max([data[i] for i in data if 'size' in data[i][0]], key=lambda x:sum([part['size'] for part in x]))
        vids, size = [t["k"] for t in temp], sum([t["size"] for t in temp])
        urls = [[n.firstChild.nodeValue.strip()
             for n in
                parseString(
                    get_html('http://ct.v2.tudou.com/f?id=%s' % vid))
                .getElementsByTagName('f')][0]
            for vid in vids]
        ext = r1(r'http://[\w.]*/(\w+)/[\w.]*', urls[0])
        self.stream_types.append('current')
        self.streams['current'] = {'container': ext, 'video_profile': 'current', 'src' : urls, 'size': size}

    def parse_playlist(self):
        aid = r1('http://www.tudou.com/playlist/p/a(\d+)(?:i\d+)?\.html', url)
        html = get_decoded_html(url)
        if not aid:
            aid = r1(r"aid\s*[:=]\s*'(\d+)'", html)
        if re.match(r'http://www.tudou.com/albumcover/', url):
            atitle = r1(r"title\s*:\s*'([^']+)'", html)
        elif re.match(r'http://www.tudou.com/playlist/p/', url):
            atitle = r1(r'atitle\s*=\s*"([^"]+)"', html)
        else:
            raise NotImplementedError(url)
        assert aid
        assert atitle
        import json
        #url = 'http://www.tudou.com/playlist/service/getZyAlbumItems.html?aid='+aid
        url = 'http://www.tudou.com/playlist/service/getAlbumItems.html?aid='+aid
        return [(atitle + '-' + x['title'], str(x['itemId'])) for x in json.loads(get_html(url))['message']]

    def download_playlist_by_url(self, url, **kwargs):
        self.url = url
        videos = parse_playlist()
        for i, (title, id) in enumerate(videos):
            print('Processing %s of %s videos...' % (i + 1, len(videos)))
            self.download_by_vid(id, title=title, **kwargs)

site = Tudou()
download = site.download_by_url
download_playlist = site.download_playlist_by_url
