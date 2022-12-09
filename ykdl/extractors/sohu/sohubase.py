# -*- coding: utf-8 -*-

from .._common import *


class SohuBase(Extractor):

    supported_stream_types = [
        #'h2654kVid',
        #'h2654mVid',
        #'h265oriVid',
        #'h265superVid',
        #'h265highVid',
        #'h265norVid',
        'h2644kVid',
        'oriVid',
        'superVid',
        'highVid',
        'norVid'
    ]
    types_2_id = {
        'h2654kVid': '4K',
        'h2654mVid': '4K',
        'h2644kVid': '4K',
        'h265oriVid': 'BD',
        'h265superVid': 'TD',
        'h265highVid': 'HD',
        'h265norVid': 'SD',
        'oriVid': 'BD',
        'superVid': 'TD',
        'highVid': 'HD',
        'norVid': 'SD'
    }
    id_2_profile = {
        '4K': '4K',
        'BD': '原画',
        'TD': '超清',
        'HD': '高清',
        'SD': '标清'
    }

    def parser_info(self, info, data, stream, lvid, uid):
        if not 'allot' in data or lvid != data['id']:
            return
        stream_id = self.types_2_id[stream]
        stream_profile = self.id_2_profile[stream_id]
        host = data['allot']
        data = data['data']
        size = sum(map(int, data['clipsBytes']))
        urls = []
        assert len(data['clipsURL']) == len(data['clipsBytes']) == len(data['su'])
        for new, ck, in zip(data['su'], data['ck']):
            if urlparse(new).netloc == '':
                url = get_response('https://{host}/ip'.format(**vars()),
                                   params={
                                       'ch': data['ch'],
                                       'num': data['num'],
                                       'new': new,
                                       'key': ck,
                                       'uid': uid,
                                       'prod': 'h5n',
                                       'pt': 1,
                                       'pg': 2,
                                   }).json()['servers'][0]['url']
            else:
                url = new
            urls.append(url)
        info.streams[stream_id] = {
            'container': 'mp4',
            'profile': stream_profile,
            'src' : urls,
            'size': size
        }

    def fetch_info(self, vid):
        self.apiparams['vid'] = vid
        return get_response(self.apiurl, params=self.apiparams).json()

    def prepare_mid(self):
        mid = match1(self.url, '\d/(\d+)\.s?html',
                              r'\b[bv]?id=(\d+)',
                               'share_play.html#(\d+)_')
        if mid is None:
            html = get_content(self.url)
            mid = match1(html, r'\b[bv]id\s*[=:]\s*["\']?(\d+)',
                               r'(?:&|\x26)[bv]?id=(\d+)'
                                '/(\d+)/v\.swf')
        return mid

    def prepare(self):
        info = MediaInfo(self.name)
        # this is needless now, uid well be registered in the the following code
        #info.extra['header'] = 'Range: '

        data = self.fetch_info(self.mid)
        assert data['status'] == 1, data

        # report
        now = time.time()
        uid = int(now * 1000)
        get_response('http://z.m.tv.sohu.com/h5_cc.gif',
                     params={
                         'vid': self.mid,
                         'url': self.url,
                         'refer': self.url,
                         't': int(now),
                         'uid': uid,
                         #'nid': nid,
                         #'pid': pid,
                         #'screen': '1366x768',
                         #'channeled': channeled,
                         #'MTV_SRC': MTV_SRC,
                         #'position': 'page_adbanner',
                         #'op': 'click',
                         #'details': '{}',
                         #'os': 'linux',
                         #'platform': 'linux',
                         #'passport': '',
                     })

        _data = data['data']
        info.title = _data['tvName']
        for stream in self.supported_stream_types:
            lvid = _data.get(stream)
            if lvid == 0 or not lvid:
                continue
            if lvid != self.mid:
                data = self.fetch_info(lvid)
            self.parser_info(info, data, stream, lvid, uid)

        return info
