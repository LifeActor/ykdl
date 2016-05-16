#!/usr/bin/env python

from ..common import *
from ..extractor import VideoExtractor

class YouTube(VideoExtractor):
    name = "YouTube"

    supported_stream_types = [ '38', '46', '37', '45', '22', '120', '44', '35', '43', '34','18', '6','13', '5','36', '17']

    # YouTube media encoding options, in descending quality order.
    # http://en.wikipedia.org/wiki/YouTube#Quality_and_codecs. Retrieved July 17, 2014.
    stream_types_DONOT_USE = [
        {'itag': '38', 'container': 'MP4', 'video_resolution': '3072p', 'video_encoding': 'H.264', 'video_profile': 'High', 'video_bitrate': '3.5-5', 'audio_encoding': 'AAC', 'audio_bitrate': '192'},
        #{'itag': '85', 'container': 'MP4', 'video_resolution': '1080p', 'video_encoding': 'H.264', 'video_profile': '3D', 'video_bitrate': '3-4', 'audio_encoding': 'AAC', 'audio_bitrate': '192'},
        {'itag': '46', 'container': 'WebM', 'video_resolution': '1080p', 'video_encoding': 'VP8', 'video_profile': '', 'video_bitrate': '', 'audio_encoding': 'Vorbis', 'audio_bitrate': '192'},
        {'itag': '37', 'container': 'MP4', 'video_resolution': '1080p', 'video_encoding': 'H.264', 'video_profile': 'High', 'video_bitrate': '3-4.3', 'audio_encoding': 'AAC', 'audio_bitrate': '192'},
        #{'itag': '102', 'container': 'WebM', 'video_resolution': '720p', 'video_encoding': 'VP8', 'video_profile': '3D', 'video_bitrate': '', 'audio_encoding': 'Vorbis', 'audio_bitrate': '192'},
        {'itag': '45', 'container': 'WebM', 'video_resolution': '720p', 'video_encoding': 'VP8', 'video_profile': '', 'video_bitrate': '2', 'audio_encoding': 'Vorbis', 'audio_bitrate': '192'},
        #{'itag': '84', 'container': 'MP4', 'video_resolution': '720p', 'video_encoding': 'H.264', 'video_profile': '3D', 'video_bitrate': '2-3', 'audio_encoding': 'AAC', 'audio_bitrate': '192'},
        {'itag': '22', 'container': 'MP4', 'video_resolution': '720p', 'video_encoding': 'H.264', 'video_profile': 'High', 'video_bitrate': '2-3', 'audio_encoding': 'AAC', 'audio_bitrate': '192'},
        {'itag': '120', 'container': 'FLV', 'video_resolution': '720p', 'video_encoding': 'H.264', 'video_profile': 'Main@L3.1', 'video_bitrate': '2', 'audio_encoding': 'AAC', 'audio_bitrate': '128'}, # Live streaming only
        {'itag': '44', 'container': 'WebM', 'video_resolution': '480p', 'video_encoding': 'VP8', 'video_profile': '', 'video_bitrate': '1', 'audio_encoding': 'Vorbis', 'audio_bitrate': '128'},
        {'itag': '35', 'container': 'FLV', 'video_resolution': '480p', 'video_encoding': 'H.264', 'video_profile': 'Main', 'video_bitrate': '0.8-1', 'audio_encoding': 'AAC', 'audio_bitrate': '128'},
        #{'itag': '101', 'container': 'WebM', 'video_resolution': '360p', 'video_encoding': 'VP8', 'video_profile': '3D', 'video_bitrate': '', 'audio_encoding': 'Vorbis', 'audio_bitrate': '192'},
        #{'itag': '100', 'container': 'WebM', 'video_resolution': '360p', 'video_encoding': 'VP8', 'video_profile': '3D', 'video_bitrate': '', 'audio_encoding': 'Vorbis', 'audio_bitrate': '128'},
        {'itag': '43', 'container': 'WebM', 'video_resolution': '360p', 'video_encoding': 'VP8', 'video_profile': '', 'video_bitrate': '0.5', 'audio_encoding': 'Vorbis', 'audio_bitrate': '128'},
        {'itag': '34', 'container': 'FLV', 'video_resolution': '360p', 'video_encoding': 'H.264', 'video_profile': 'Main', 'video_bitrate': '0.5', 'audio_encoding': 'AAC', 'audio_bitrate': '128'},
        #{'itag': '82', 'container': 'MP4', 'video_resolution': '360p', 'video_encoding': 'H.264', 'video_profile': '3D', 'video_bitrate': '0.5', 'audio_encoding': 'AAC', 'audio_bitrate': '96'},
        {'itag': '18', 'container': 'MP4', 'video_resolution': '270p/360p', 'video_encoding': 'H.264', 'video_profile': 'Baseline', 'video_bitrate': '0.5', 'audio_encoding': 'AAC', 'audio_bitrate': '96'},
        {'itag': '6', 'container': 'FLV', 'video_resolution': '270p', 'video_encoding': 'Sorenson H.263', 'video_profile': '', 'video_bitrate': '0.8', 'audio_encoding': 'MP3', 'audio_bitrate': '64'},
        #{'itag': '83', 'container': 'MP4', 'video_resolution': '240p', 'video_encoding': 'H.264', 'video_profile': '3D', 'video_bitrate': '0.5', 'audio_encoding': 'AAC', 'audio_bitrate': '96'},
        {'itag': '13', 'container': '3GP', 'video_resolution': '', 'video_encoding': 'MPEG-4 Visual', 'video_profile': '', 'video_bitrate': '0.5', 'audio_encoding': 'AAC', 'audio_bitrate': ''},
        {'itag': '5', 'container': 'FLV', 'video_resolution': '240p', 'video_encoding': 'Sorenson H.263', 'video_profile': '', 'video_bitrate': '0.25', 'audio_encoding': 'MP3', 'audio_bitrate': '64'},
        {'itag': '36', 'container': '3GP', 'video_resolution': '240p', 'video_encoding': 'MPEG-4 Visual', 'video_profile': 'Simple', 'video_bitrate': '0.175', 'audio_encoding': 'AAC', 'audio_bitrate': '36'},
        {'itag': '17', 'container': '3GP', 'video_resolution': '144p', 'video_encoding': 'MPEG-4 Visual', 'video_profile': 'Simple', 'video_bitrate': '0.05', 'audio_encoding': 'AAC', 'audio_bitrate': '24'},
    ]

    def decipher(js, s):
        def tr_js(code):
            code = re.sub(r'function', r'def', code)
            code = re.sub(r'(\W)(as|if|in|is|or)\(', r'\1_\2(', code)
            code = re.sub(r'\$', '_dollar', code)
            code = re.sub(r'\{', r':\n\t', code)
            code = re.sub(r'\}', r'\n', code)
            code = re.sub(r'var\s+', r'', code)
            code = re.sub(r'(\w+).join\(""\)', r'"".join(\1)', code)
            code = re.sub(r'(\w+).length', r'len(\1)', code)
            code = re.sub(r'(\w+).slice\((\w+)\)', r'\1[\2:]', code)
            code = re.sub(r'(\w+).splice\((\w+),(\w+)\)', r'del \1[\2:\2+\3]', code)
            code = re.sub(r'(\w+).split\(""\)', r'list(\1)', code)
            return code

        js = js.replace('\n', ' ')
        f1 = match1(js, r'\w+\.sig\|\|([$\w]+)\(\w+\.\w+\)')
        f1def = match1(js, r'function %s(\(\w+\)\{[^\{]+\})' % re.escape(f1)) or \
                match1(js, r'\W%s=function(\(\w+\)\{[^\{]+\})' % re.escape(f1))
        f1def = re.sub(r'([$\w]+\.)([$\w]+\(\w+,\d+\))', r'\2', f1def)
        code = tr_js(f1def)
        f2s = set(re.findall(r'([$\w]+)\(\w+,\d+\)', f1def))
        for f2 in f2s:
            f2e = re.escape(f2)
            f2def = re.search(r'[^$\w]%s:function\((\w+,\w+)\)(\{[^\{\}]+\})' % f2e, js)
            if f2def:
                f2def = 'function {}({}){}'.format(f2e, f2def.group(1), f2def.group(2))
            else:
                f2def = re.search(r'[^$\w]%s:function\((\w+)\)(\{[^\{\}]+\})' % f2e, js)
                f2def = 'function {}({},b){}'.format(f2e, f2def.group(1), f2def.group(2))
            f2 = re.sub(r'(\W)(as|if|in|is|or)\(', r'\1_\2(', f2)
            f2 = re.sub(r'\$', '_dollar', f2)
            code = code + 'global %s\n' % f2 + tr_js(f2def)

        f1 = re.sub(r'(as|if|in|is|or)', r'_\1', f1)
        f1 = re.sub(r'\$', '_dollar', f1)
        code = code + 'sig=%s(s)' % f1
        exec(code, globals(), locals())
        return locals()['sig']

    def get_url_from_vid(vid):
        return 'https://youtu.be/{}'.format(vid)

    def get_vid_from_url(url):
        """Extracts video ID from URL.
        """
        return match1(url, r'youtu\.be/([^/]+)') or \
          match1(url, r'youtube\.com/embed/([^/?]+)') or \
          match1(url, r'youtube\.com/v/([^/?]+)') or \
          parse_query_param(url, 'v') or \
          parse_query_param(parse_query_param(url, 'u'), 'v')

    def get_playlist_id_from_url(url):
        """Extracts playlist ID from URL.
        """
        return parse_query_param(url, 'list') or \
          parse_query_param(url, 'p')

    def download_playlist_by_url(self, url, param, **kwargs):
        self.url = url

        playlist_id = self.__class__.get_playlist_id_from_url(self.url)
        if playlist_id is None:
            log.wtf('[Failed] Unsupported URL pattern.')

        video_page = get_content('https://www.youtube.com/playlist?list=%s' % playlist_id)
        from html.parser import HTMLParser
        videos = sorted([HTMLParser().unescape(video)
                         for video in re.findall(r'<a href="(/watch\?[^"]+)"', video_page)
                            if parse_query_param(video, 'index')],
                        key=lambda video: parse_query_param(video, 'index'))
        self.title = re.search(r'<meta name="title" content="([^"]+)"', video_page).group(1)

        for video in videos:
            vid = parse_query_param(video, 'v')
            index = parse_query_param(video, 'index')
            self.download_by_url(self.__class__.get_url_from_vid(vid), param, index=index, **kwargs)

    def prepare(self, **kwargs):

        if not self.vid and self.url:
            self.vid = self.__class__.get_vid_from_url(self.url)

            if self.vid is None:
                self.download_playlist_by_url(self.url, **kwargs)
                exit(0)

        video_info = parse.parse_qs(get_content('https://www.youtube.com/get_video_info?video_id={}'.format(self.vid)))

        if 'status' not in video_info:
            log.wtf('[Failed] Unknown status.')

        elif video_info['status'] == ['ok']:
            if 'use_cipher_signature' not in video_info or video_info['use_cipher_signature'] == ['False']:
                self.title = parse.unquote_plus(video_info['title'][0])
                stream_list = video_info['url_encoded_fmt_stream_map'][0].split(',')

            else:
                # Parse video page instead
                video_page = get_content('https://www.youtube.com/watch?v=%s' % self.vid)
                ytplayer_config = json.loads(re.search('ytplayer.config\s*=\s*([^\n]+?});', video_page).group(1))

                self.title = ytplayer_config['args']['title']
                self.html5player = 'https:' + ytplayer_config['assets']['js']
                stream_list = ytplayer_config['args']['url_encoded_fmt_stream_map'].split(',')

        elif video_info['status'] == ['fail']:
            if video_info['errorcode'] == ['150']:
                video_page = get_content('https://www.youtube.com/watch?v=%s' % self.vid)
                try:
                    ytplayer_config = json.loads(re.search('ytplayer.config\s*=\s*([^\n]+});ytplayer', video_page).group(1))
                except:
                    msg = re.search('class="message">([^<]+)<', video_page).group(1)
                    log.wtf('[Failed] "%s"' % msg.strip())

                if 'title' in ytplayer_config['args']:
                    # 150 Restricted from playback on certain sites
                    # Parse video page instead
                    self.title = ytplayer_config['args']['title']
                    self.html5player = 'https:' + ytplayer_config['assets']['js']
                    stream_list = ytplayer_config['args']['url_encoded_fmt_stream_map'].split(',')
                else:
                    log.wtf('[Error] The uploader has not made this video available in your country.')
                    #self.title = re.search('<meta name="title" content="([^"]+)"', video_page).group(1)
                    #stream_list = []

            elif video_info['errorcode'] == ['100']:
                log.wtf('[Failed] This video does not exist.', exit_code=int(video_info['errorcode'][0]))

            else:
                log.wtf('[Failed] %s' % video_info['reason'][0], exit_code=int(video_info['errorcode'][0]))

        else:
            log.wtf('[Failed] Invalid status.')

        for stream in stream_list:
            metadata = parse.parse_qs(stream)
            stream_itag = metadata['itag'][0]
            self.streams[stream_itag] = {
                'itag': metadata['itag'][0],
                'url': metadata['url'][0],
                'sig': metadata['sig'][0] if 'sig' in metadata else None,
                's': metadata['s'][0] if 's' in metadata else None,
                'quality': metadata['quality'][0],
                'type': metadata['type'][0],
                'mime': metadata['type'][0].split(';')[0],
                'container': mime_to_container(metadata['type'][0].split(';')[0]),
            }
        for stream in self.supported_stream_types:
            if stream in self.streams.keys():
                self.stream_types.append(stream)

    def extract(self, **kwargs):
        if not self.stream_types:
            # No stream is available
            return

        if self.param.info_only:
            for stream_id in self.stream_types:
                src = self.streams[stream_id]['url']

                if self.streams[stream_id]['sig'] is not None:
                    sig = self.streams[stream_id]['sig']
                    src += '&signature={}'.format(sig)

                elif self.streams[stream_id]['s'] is not None:
                    s = self.streams[stream_id]['s']
                    js = get_content(self.html5player)
                    sig = self.__class__.decipher(js, s)
                    src += '&signature={}'.format(sig)

                self.streams[stream_id]['src'] = [src]
                self.streams[stream_id]['size'] = urls_size(self.streams[stream_id]['src'])
            return

        stream_id = self.param.stream_id or self.stream_types[0]

        src = self.streams[stream_id]['url']

        if self.streams[stream_id]['sig'] is not None:
            sig = self.streams[stream_id]['sig']
            src += '&signature={}'.format(sig)

        elif self.streams[stream_id]['s'] is not None:
            s = self.streams[stream_id]['s']
            js = get_content(self.html5player)
            sig = self.__class__.decipher(js, s)
            src += '&signature={}'.format(sig)

        self.streams[stream_id]['src'] = [src]
        self.streams[stream_id]['size'] = urls_size(self.streams[stream_id]['src'])

site = YouTube()
download = site.download_by_url
download_playlist = site.download_playlist_by_url
