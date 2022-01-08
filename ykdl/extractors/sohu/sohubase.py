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

    def parser_info(self, video, info, stream, lvid, uid):
        if not 'allot' in info or lvid != info['id']:
            return
        stream_id = self.types_2_id[stream]
        stream_profile = self.id_2_profile[stream_id]
        host = info['allot']
        data = info['data']
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
        video.streams[stream_id] = {
            'container': 'mp4',
            'video_profile': stream_profile,
            'src': urls,
            'size' : size
        }

    def fetch_info(self, vid):
        self.apiparams['vid'] = vid
        return get_response(self.apiurl, params=self.apiparams).json()

    def prepare(self):
        if self.url and not self.vid:
            self.vid = match1(self.url, '\W[b|v]?id=(\d+)',
                                        'share_play.html#(\d+)_')
            if not self.vid:
                html = get_content(self.url)
                self.vid = match1(html, '/(\d+)/v\.swf',
                                        'vid="(\d+)"',
                                        '&id=(\d+)')

        info = self.fetch_info(self.vid)
        if info['status'] == 6:
            from .my import site
            self.name = site.name
            self.apiurl = site.apiurl
            self.apiparams = site.apiparams
            info = self.fetch_info(self.vid)

        video = MediaInfo(self.name)
        # this is needless now, uid well be registered in the the following code
        #video.extra['header'] = 'Range: '
        if info['status'] == 1:
            now = time.time()
            uid = int(now * 1000)
            get_response('http://z.m.tv.sohu.com/h5_cc.gif',
                         params={
                             'vid': self.vid,
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

            data = info['data']
            video.title = data['tvName']
            for stream in self.supported_stream_types:
                lvid = data.get(stream)
                if lvid == 0 or not lvid:
                    continue
                if lvid != self.vid:
                    _info = self.fetch_info(lvid)
                else:
                    _info = info

                self.parser_info(video, _info, stream, lvid, uid)
        return video
