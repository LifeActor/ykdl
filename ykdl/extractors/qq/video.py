# -*- coding: utf-8 -*-

from .._common import *


PLAYER_PLATFORMS = [11, 2, 1]
PLAYER_VERSION = '3.2.19.333'


def qq_get_final_url(url, vid, fmt_id, filename, fvkey, platform):
    params = {
        'appver': PLAYER_VERSION,
        'otype': 'json',
        'platform': platform,
        'filename': filename,
        'vid': vid,
        'format': fmt_id,
    }

    data = get_response('https://vv.video.qq.com/getkey', params=params).json()
    vkey = data.get('key', fvkey)
    if vkey:
        url = '{url}{filename}?vkey={vkey}'.format(**vars())
    else:
        url = None
    vip = data.get('msg') == 'not pay'

    return url, vip

class QQ(Extractor):

    name = '腾讯视频 (QQ)'
    vip = None

    stream_2_id = {
        'fhd': 'BD',  #
        'shd': 'TD',  # null
         'hd': 'HD',
        'mp4': 'HD',
        'flv': 'HD',
         'sd': 'SD',
        'msd': 'LD'
    }


    def get_streams_info(self, vid, profile='shd'):
        for PLAYER_PLATFORM in PLAYER_PLATFORMS.copy():
            data = get_response('https://vv.video.qq.com/getinfo',
                                params={
                                    'otype': 'json',
                                    'platform': PLAYER_PLATFORM,
                                    'vid': vid,
                                    'defnpayver': 1,
                                    'appver': PLAYER_VERSION,
                                    'defn': profile,
                                }).json()
            if 'msg' in data:
                continue

            #if PLAYER_PLATFORMS and \
            #        profile == 'shd' and \
            #        '"name":"shd"' not in resp.text and \
            #        '"name":"fhd"' not in resp.text:
            #    for infos in self.get_streams_info(vid, 'hd'):
            #        yield infos
            #    return

            break

        assert 'msg' not in data, data['msg']
        video = data['vl']['vi'][0]
        fn = video['fn']
        title = video['ti']
        td = float(video['td'])
        fvkey = video.get('fvkey')
        # Not to be absolutely accuracy.
        #fp2p = data.get('fp2p')
        iflag = video.get('iflag')
        pl = video.get('pl')
        self.limit = bool(iflag or pl)
        self.vip = video['drm']

        # Priority for range fetch.
        cdn_url_1 = cdn_url_2 = cdn_url_3 = None
        for cdn in video['ul']['ui']:
            cdn_url = cdn['url']
            if 'vip' in cdn_url:
                continue
            # 'video.dispatch.tc.qq.com' supported keep-alive link.
            if cdn_url.startswith('http://video.dispatch.tc.qq.com/'):
                cdn_url_3 = cdn_url
            # IP host.
            elif match1(cdn_url, '(^http://[0-9\.]+/)'):
                if not cdn_url_2:
                    cdn_url_2 = cdn_url
            elif not cdn_url_1:
                cdn_url_1 = cdn_url
        if self.limit:
            cdn_url = cdn_url_3 or cdn_url_1 or cdn_url_2
        else:
            cdn_url = cdn_url_1 or cdn_url_2 or cdn_url_3
        #cdn_url = cdn_url_1 or cdn_url_2 or cdn_url_3

        dt = cdn['dt']
        if dt == 1:
            ext = 'flv'
        elif dt == 2:
            ext = 'mp4'
        else:
            ext = fn.split('.')[-1]

        _num_clips = video['cl']['fc']
        #self.limit = video.get('type', 0) > 1000
        #if self.limit:
        #    if _num_clips > 1:
        #        self.logger.warning('Only parsed first video part!')
        #    for fmt in data['fl']['fi']:
        #        if fmt['sl']:
        #            fmt_name = fmt['name']
        #            fmt_cname = fmt['cname']
        #            break
        #    fns = fn.split('.')
        #    fns.insert(-1, '1')
        #    filename = '.'.join(fns)
        #    url = '{}{}?vkey={}'.format(cdn_url, filename, fvkey)
        #    size = video['cl']['ci'][0]['cs'] # not correct, real size is smaller.
        #    rate = size // float(video['cl']['ci'][0]['cd'])
        #    yield title, fmt_name, fmt_cname, ext, [url], size, rate
        #    return

        for fmt in data['fl']['fi']:
            fmt_id = fmt['id']
            fmt_name = fmt['name']
            fmt_cname = fmt['cname']
            size = fmt['fs']
            rate = size // td

            fns = fn.split('.')
            fmt_id_num = int(fmt_id)
            fmt_id_prefix = None
            num_clips = 0

            if fmt_id_num > 100000:
                fmt_id_prefix = 'm'
            elif fmt_id_num > 10000:
                fmt_id_prefix = 'p'
                num_clips = _num_clips or 1
            if fmt_id_prefix:
                fmt_id_name = fmt_id_prefix + str(fmt_id_num % 10000)
                if fns[1][0] in ('p', 'm') and not fns[1].startswith('mp'):
                    fns[1] = fmt_id_name
                else:
                    fns.insert(1, fmt_id_name)
            elif fns[1][0] in ('p', 'm') and not fns[1].startswith('mp'):
                del fns[1]

            urls =[]

            if num_clips == 0:
                filename = '.'.join(fns)
                url, vip = qq_get_final_url(cdn_url, vid, fmt_id,
                                            filename, fvkey, PLAYER_PLATFORM)
                if vip:
                    self.vip = vip
                elif url:
                    urls.append(url)
            else:
                fns.insert(-1, '1')
                for idx in range(1, num_clips + 1):
                    fns[-2] = str(idx)
                    filename = '.'.join(fns)
                    url, vip = qq_get_final_url(cdn_url, vid, fmt_id,
                                            filename, fvkey, PLAYER_PLATFORM)
                    if vip:
                        self.vip = vip
                        break
                    elif url:
                        urls.append(url)

            yield title, fmt_name, fmt_cname, ext, urls, size, rate

    def list_only(self):
        cid, vid = self.mid
        return cid and not vid

    @staticmethod
    def format_mid(mid):
        # [0] cover id, length 15
        # [1] video id, length 11
        if not isinstance(mid, tuple):
            mid = mid, None
        mid = mid[:2]
        if len(mid) == 1:
            mid += (None, )
        assert any(mid)
        if mid[0] and len(mid[0]) == 11:
            mid = mid[::-1]
        assert not mid[0] or len(mid[0]) == 15
        assert not mid[1] or len(mid[1]) == 11
        return mid

    def parse_html(self):
        html = get_content(self.url)
        return match1(html, r'\bvid[\"\']?\s*[=:]\s*[\"\']?(\w+)')

    def prepare_mid(self):
        mid = matchm(self.url, '/x/page/(\w+)\.html',
                               r'\bvid=(\w+)',
                               '/x/cover/(\w+)\.html',
                               '/x/cover/(\w+)/(\w+)\.html',
                               '/(\w+)/?$')
        if any(mid):
            return mid
        return self.parse_html()

    def prepare(self):
        info = MediaInfo(self.name)

        cid, vid = self.mid
        if vid is None:
            if self.url is None:
                self.url = 'https://v.qq.com/x/cover/{cid}.html'.format(**vars())
            vid = self.parse_html()

        video_rate = {}
        for (title, fmt_name, stream_profile, ext, urls, size, rate) in self.get_streams_info(vid):
            if urls:
                stream_id = self.stream_2_id[fmt_name]
                info.streams[stream_id] = {
                    'container': ext,
                    'profile': stream_profile,
                    'src' : urls,
                    'size': size
                }
                video_rate[stream_id] = rate

        if self.vip:
            self.logger.warning('This is a VIP video!')
            #self.limit = False

        #if self.limit:
        #    # Downloading some videos is very slow, use multithreading range fetch to speed up.
        #    # Only for video players now.
        #    info.extra['rangefetch'] = {
        #        'first_size': 1024 * 16,
        #        'max_size': 1024 * 32,
        #        'threads': 10,
        #        'video_rate': video_rate
        #    }
        #    self.logger.warning('This is a restricted video!')

        info.title = title
        info.extra.referer = 'https://v.qq.com/'
        return info

    def prepare_list(self):
        cid, vid = self.mid
        html = get_content('https://v.qq.com/x/cover/{cid}.html'.format(**vars()))
        vids = match1(html, '"video_ids":(\[.+?\])')
        if vids:
            vids = json.loads(vids)
        else:
            vids = matchall(html, r'\bdata-vid="(\w+)"') or \
                   matchall(html, '"vid":"(\w+)"')
        # FIXME some covers are reversed
        self.set_index(vid, vids)
        return vids

site = QQ()
