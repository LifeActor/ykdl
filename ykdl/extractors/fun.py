# -*- coding: utf-8 -*-

from ._common import *

import binascii


mozecname = []

def fetch_mozecname(vid):
    # vid: seems non-interrelated with result

    global mozecname
    if len(mozecname) == 4:
        return

    digits = list('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')

    def i2b(d):
        if base == 10:
            return str(d)
        b = []
        while d:
            d, m = divmod(d, base)
            b.append(digits[m])
        return ''.join(b[::-1]) or '0'

    def b2i(text):
        try:
            i = int(text, base)
        except ValueError:
            i = p = 0
            for d in text[::-1]:
                i += digits.index(d) * base ** p
                p += 1
        return i

    def encrypt(text):
        '''fake, only for existed texts'''
        return i2b(keys_dict[text])

    def decrypt(text):
        return keys_list[b2i(text)] or text

    html = get_content('https://m.fun.tv/vplay/?vid=' + vid)
    for path in matchall(html[:html.find('</head>')],
                         'src="(/static/js/v12/pkg/m\w{4}_v12_\w{9}.js)"'):
        js = get_content('https://m.fun.tv' + path).strip()
        crypt, base, _, keys, sep = re.search(
                r"}\('(.+?)[^\\]',(\d+),(\d+),'(.+?)'\.split\('(.)'", js).groups()
        base = int(base)
        keys_list = keys.split(sep)
        keys_dict = {k: i for i, k in enumerate(keys_list)}
        pattern = '\\.'.join(encrypt(text)
                  for text in ['document', 'mozEcName', 'push']) + '\("(\w+)'
        mozecname += [decrypt(text) for text in matchall(crypt, pattern)]
    site.logger.debug('mozEcName: %s', mozecname)
    mozecname = {int(m[-1]): int(m[:-1], 16) for m in mozecname}

def decrypt(obj):
    '''
    decrypt infohash & token
    https://github.com/SeaHOH/ykdl/issues/278#issuecomment-581010230
    '''

    def i(t):
        if match1(t, '^(\w{27}0)$'):
            a = o(base64.b64decode(t[:-1] + '='))
            return binascii.hexlify(a.encode()).upper()
        return o(base64.b64decode(t[2:]))

    def o(t):
        e = (n(t[i], t[i + 1]) for i in range(0, len(t) - 1, 2))
        e = sum(e, ()) + (t[-1], )
        return bytes(e).decode('latin_1')

    def n(t, e):
        return ((t * mozecname[0] + e * mozecname[2]) & 0xff,
                (t * mozecname[1] + e * mozecname[3]) & 0xff)

    def c(e):
        return match1(e, '^(\w{41})$') and \
               sum(int(e[r], 16) for r in range(40)) & 15 == int(e[-1], 16)

    for p in ['_prev', '']:
        e = i(obj['infohash' + p])
        if not c(e):
            continue
        obj['infohash'] = e[:-1]
        obj['token'] = base64.b64encode(i(obj['token' + p]).encode()).decode()
        return


class Funshion(Extractor):
    name = '风行网'

    quality_2_id = {
         'shd': 'BD',  # vip, not used
        'sdvd': 'TD',
          'hd': 'HD',
         'dvd': 'SD',
          'tv': 'LD'
    }

    def prepare(self):
        info = MediaInfo(self.name)

        html = get_content(self.url)
        MID = html.find('"mediaid":') > 0
        title = MID and match1(html,
                            'class="pl-tit fix">\s+<a class="tit"[^>]+>([^<]+)')
        ctitle = match1(html, 'class="cru-tit" title="([^"]+)')
        if title and ctitle and title not in ctitle:
            ctitle = ' '.join([title, ctitle])
        info.title = ctitle
        vid = match1(self.url, '[/\.]v-(\d+)') or \
              match1(html,
                     'class="download_pc tool_cli_link"[\s\S]+?data-vid="(\d+)')

        ct = int(time.time())
        fudid = '{}{:x}'.format(ct - 5, random.randint(1 << 16, (1 << 20) - 1))
        data = get_response(MID and
                            'https://pm.funshion.com/v7/media/play/?' or
                            'https://pv.funshion.com/v7/video/play/?',
                            params={
                                'id': vid,
                                'ves': 1,
                                'cl': 'web',
                                'uc': 111,
                                'fudid': fudid,
                                'token': '',
                                'code': 'play-vipbanner',
                                'ctime': ct,
                                'app_code': 'web'
                            }).json()
        assert data['retcode'] == '200', data['retmsg']

        fetch_mozecname(vid)
        for vinfos in data['playlist']:
            stream_id = self.quality_2_id[vinfos['code']]
            for vinfo in vinfos['playinfo']:
                if vinfo.get('isvip') == '1':
                    continue
                if vinfo['codec'] == 'h.264':
                    codec = '-h264'
                elif vinfo['codec'] == 'h.265':
                    codec = '-h265'
                elif vinfo['codec'] == 'h.265_hls_ts':
                    codec = '-h265t'
                else:
                    codec = ''
                decrypt(vinfo)
                url = (
                    'https://jobsfe.funshion.com/play/v1/mp4/{}.mp4?'.
                    format(vinfo['infohash']) +
                    urlencode({
                        'token': vinfo['token'],
                        'vf': vinfo['vf']
                    }))
                info.streams[stream_id + codec] = {
                    'container': 'mp4',
                    'profile': vinfos['name'],
                    'src' : [url],
                    'size': int(vinfo['filesize'])
                }

        return info

site = Funshion()
