#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..common import *
from ..extractor import VideoExtractor

import base64
import time
import urllib.parse
import math
import pdb

class Youku(VideoExtractor):
    name = "优酷 (Youku)"

    supported_stream_types = [ 'hd3', 'hd2', 'mp4', 'flvhd','flv', '3gphd']

    stream_2_container = {'hd3': 'flv', 'hd2':'flv', 'mp4':'mp4', 'flvhd':'flv', 'flv': 'flv', '3gphd': 'mp4'}

    stream_2_profile = {'hd3': '1080P', 'hd2':'超清', 'mp4':'高清', 'flvhd':'高清', 'flv': '标清', '3gphd': '高清（3GP）'}

    def trans_e(a, c):
        f = h = 0
        b = list(range(256))
        result = ''
        while h < 256:
            f = (f + b[h] + ord(a[h % len(a)])) % 256
            b[h], b[f] = b[f], b[h]
            h += 1
        q = f = h = 0
        while q < len(c):
            h = (h + 1) % 256
            f = (f + b[h]) % 256
            b[h], b[f] = b[f], b[h]
            if isinstance(c[q], int):
                result += chr(c[q] ^ b[(b[h] + b[f]) % 256])
            else:
                result += chr(ord(c[q]) ^ b[(b[h] + b[f]) % 256])
            q += 1

        return result

    def generate_ep_prepare(streamfileids,seed,ep):  #execute once
        f_code_1 = 'becaf9be'
        def trans_e(a, c):
            f = h = 0
            b = list(range(256))
            result = ''
            while h < 256:
                f = (f + b[h] + ord(a[h % len(a)])) % 256
                b[h], b[f] = b[f], b[h]
                h += 1
            q = f = h = 0
            while q < len(c):
                h = (h + 1) % 256
                f = (f + b[h]) % 256
                b[h], b[f] = b[f], b[h]
                if isinstance(c[q], int):
                    result += chr(c[q] ^ b[(b[h] + b[f]) % 256])
                else:
                    result += chr(ord(c[q]) ^ b[(b[h] + b[f]) % 256])
                q += 1

            return result

        def getFileIdMixed(seed):
            mixed=[]
            source = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOP' +'QRSTUVWXYZ/\\:._-1234567890'
            len1 = len(source)
            for i in range(0,len1):
                seed = (seed * 211 + 30031) % 65536;
                index = math.floor(seed / 65536 * len(source));
                mixed += source[index]
                source = source.replace(source[index], '');
            return mixed

        def getFileId(fileId,seed):
            mixed = getFileIdMixed(seed)
            ids = fileId.split('*')
            len1 = len(ids) - 1
            realId = ''
            for i in range(0,len1):
                idx = int(ids[i])
                realId += mixed[idx]
            return realId



        e_code = trans_e(f_code_1, base64.b64decode(bytes(ep, 'ascii')))

        sid, token = e_code.split('_')
        fileId0 = getFileId(streamfileids, seed)

        return fileId0,sid,token

    def generate_ep(no,fileId0,sid,token):
        def trans_e(a, c):
            f = h = 0
            b = list(range(256))
            result = ''
            while h < 256:
                f = (f + b[h] + ord(a[h % len(a)])) % 256
                b[h], b[f] = b[f], b[h]
                h += 1
            q = f = h = 0
            while q < len(c):
                h = (h + 1) % 256
                f = (f + b[h]) % 256
                b[h], b[f] = b[f], b[h]
                if isinstance(c[q], int):
                    result += chr(c[q] ^ b[(b[h] + b[f]) % 256])
                else:
                    result += chr(ord(c[q]) ^ b[(b[h] + b[f]) % 256])
                q += 1

            return result

        f_code_2 = 'bf7e5f01'

        number = hex(int(str(no),10))[2:].upper()
        if len(number) == 1:
            number = '0' + number
        fileId = fileId0[0:8] + number + fileId0[10:]

        ep = urllib.parse.quote(base64.b64encode(''.join(trans_e(f_code_2,sid+'_'+fileId+'_'+token)).encode('latin1')),safe='~()*!.\'')
        return fileId,ep

    def parse_m3u8(m3u8):
        return re.findall('(http://[^\r]+)\r',m3u8)

    def get_vid_from_url(url):
        """Extracts video ID from URL.
        """
        return match1(url, r'youku\.com/v_show/id_([a-zA-Z0-9=]+)') or \
          match1(url, r'player\.youku\.com/player\.php/sid/([a-zA-Z0-9=]+)/v\.swf') or \
          match1(url, r'loader\.swf\?VideoIDS=([a-zA-Z0-9=]+)') or \
          match1(url, r'player\.youku\.com/embed/([a-zA-Z0-9=]+)')

    def get_playlist_id_from_url(url):
        """Extracts playlist ID from URL.
        """
        return match1(url, r'youku\.com/playlist_show/id_([a-zA-Z0-9=]+)')

    def download_playlist_by_url(self, url, **kwargs):
        self.url = url

        playlist_id = self.__class__.get_playlist_id_from_url(self.url)
        if playlist_id is None:
            log.wtf('[Failed] Unsupported URL pattern.')

        video_page = get_content('http://www.youku.com/playlist_show/id_%s' % playlist_id)
        videos = set(re.findall(r'href="(http://v\.youku\.com/[^?"]+)', video_page))

        for extra_page_url in set(re.findall('href="(http://www\.youku\.com/playlist_show/id_%s_[^?"]+)' % playlist_id, video_page)):
            extra_page = get_content(extra_page_url)
            videos |= set(re.findall(r'href="(http://v\.youku\.com/[^?"]+)', extra_page))

        self.title = re.search(r'<meta name="title" content="([^"]+)"', video_page).group(1)
        self.p_playlist()
        for video in videos:
            index = parse_query_param(video, 'f')
            self.__class__().download_by_url(video, index=index, **kwargs)

    def prepare(self, **kwargs):
        assert self.url or self.vid

        if self.url and not self.vid:
            self.vid = self.__class__.get_vid_from_url(self.url)

            if self.vid is None:
                self.download_playlist_by_url(self.url, **kwargs)
                exit(0)

        meta = json.loads(get_html('http://v.youku.com/player/getPlayList/VideoIDS/%s/Pf/4/ctype/12/ev/1' % self.vid))
        if not meta['data']:
            log.wtf('[Failed] Video not found.')
        metadata0 = meta['data'][0]

        if 'error_code' in metadata0 and metadata0['error_code']:
            if metadata0['error_code'] == -6:
                log.w('[Warning] This video is password protected.')
                self.password_protected = True
                password = input(log.sprint('Password: ', log.YELLOW))
                meta = json.loads(get_html('http://v.youku.com/player/getPlayList/VideoIDS/%s/Pf/4/ctype/12/ev/1/password/' % self.vid + password))
                if not meta['data']:
                    log.wtf('[Failed] Video not found.')
                metadata0 = meta['data'][0]

        if 'error_code' in metadata0 and metadata0['error_code']:
            if metadata0['error_code'] == -8:
                log.w('[Warning] This video can only be streamed within Mainland China!')
                log.w('Use \'-y\' to specify a proxy server for extracting stream data.\n')

        self.title = metadata0['title']
        self.metadata = metadata0
        self.ep = metadata0['ep']
        self.ip = metadata0['ip']
##
        self.seed = metadata0['seed']

##
        if 'dvd' in metadata0 and 'audiolang' in metadata0['dvd']:
            self.audiolang = metadata0['dvd']['audiolang']
            for i in self.audiolang:
                i['url'] = 'http://v.youku.com/v_show/id_{}'.format(i['vid'])

        for stream_type in self.supported_stream_types:
            if stream_type in metadata0['streamsizes']:
                stream_size = int(metadata0['streamsizes'][stream_type])
                self.streams[stream_type] = {'container': self.stream_2_container[stream_type],'video_profile': self.stream_2_profile[stream_type], 'size': stream_size}
                self.stream_types.append(stream_type)

        if not self.streams:
            for stream_type in self.supported_stream_types:
                if stream_type in metadata0['streamtypes_o']:
                    self.streams[stream_type] = {'container': self.stream_2_container[stream_type],'video_profile': self.stream_2_profile[stream_type]}
                    self.stream_types.append(stream_type)

    def extract(self, **kwargs):
        if 'stream_id' in kwargs and kwargs['stream_id']:
            # Extract the stream
            stream_id = kwargs['stream_id']

            if stream_id not in self.streams:
                log.e('[Error] Invalid video format.')
                log.e('Run \'-i\' command with no specific video format to view all available formats.')
                exit(2)
        else:
            # Extract stream with the best quality
            stream_id = self.stream_types[0]

        container = self.streams[stream_id]['container']
        self.streamfileids = self.metadata['streamfileids'][stream_id]

        fileId0,sid,token = self.__class__.generate_ep_prepare(self.streamfileids,self.seed,self.ep)
        m3u8 = ''
        stream_list=self.metadata['segs'][stream_id]
        for nu in range(0,len(stream_list)):
            k = stream_list[nu]['k']
            if k == -1:
                log.e('Error')
                exit()
            no = stream_list[nu]['no']
            fileId,ep  = self.__class__.generate_ep(no,fileId0,sid,token)
            #pdb.set_trace()
            m3u8  += 'http://k.youku.com/player/getFlvPath/sid/'+ sid
            m3u8+='_00/st/'+ container
            m3u8+='/fileid/'+ fileId
            m3u8+='?K='+ k
            m3u8+='&ctype=12&ev=1&token='+ token
            m3u8+='&oip='+ str(self.ip)
            m3u8+='&ep='+ ep+'\r\n'

        if not kwargs['info_only']:
            self.streams[stream_id]['src'] = self.__class__.parse_m3u8(m3u8)
            if not self.streams[stream_id]['src'] and self.password_protected:
                log.e('[Failed] Wrong password.')

site = Youku()
download = site.download_by_url
download_playlist = site.download_playlist_by_url

youku_download_by_vid = site.download_by_vid
# Used by: acfun.py bilibili.py miomio.py tudou.py
