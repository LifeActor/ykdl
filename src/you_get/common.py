#!/usr/bin/env python

import getopt
import json
import locale
import os
import platform
import re
import sys
from urllib import request, parse
from importlib import import_module

from .version import __version__
from .util import log
from .util.strings import get_filename, unescape_html
from .util.progressbar import SimpleProgressBar, PiecesProgressBar
from .util.match import match1, matchall, r1
from .util.html import *

dry_run = False
force = False
player = None
extractor_proxy = None
cookies_txt = None



if sys.stdout.isatty():
    default_encoding = sys.stdout.encoding.lower()
else:
    default_encoding = locale.getpreferredencoding().lower()

# DEPRECATED in favor of util.legitimize()
def escape_file_path(path):
    path = path.replace('/', '-')
    path = path.replace('\\', '-')
    path = path.replace('*', '-')
    path = path.replace('?', '-')
    return path

def launch_player(player, urls, size):
    import subprocess
    import shlex
    if size and size != float('inf'):
        size_kb = int(size/1024) + 1
        if 'mpv' in player:
            if size_kb > 2147483647:
                size_kb = 2147483647
            if size_kb < 1024:
                size_kb = 1024
            player += " --cache={}".format(size_kb)
        elif 'mplayer' in player:
            player += " --cache={} --cache-min=1".format(size_kb)
        else:
            log.d("your player: {} 's cache option is not supported!!".format(player))
            log.d("please report issue to https://github.com/zhangn1985/you-get/issues/5")
            log.d("thanks a lot!")
    subprocess.call(shlex.split(player) + list(urls))



def url_save(url, filepath, bar, refer = None, is_part = False, faker = False):
    file_size = url_size(url, faker = faker)

    if os.path.exists(filepath):
        if not force and file_size == os.path.getsize(filepath):
            if not is_part:
                if bar:
                    bar.done()
                print('Skipping %s: file already exists' % os.path.basename(filepath))
            else:
                if bar:
                    bar.update_received(file_size)
            return
        else:
            if not is_part:
                if bar:
                    bar.done()
                print('Overwriting %s' % os.path.basename(filepath), '...')
    elif not os.path.exists(os.path.dirname(filepath)):
        os.mkdir(os.path.dirname(filepath))

    temp_filepath = filepath + '.download' if file_size!=float('inf') else filepath
    received = 0
    if not force:
        open_mode = 'ab'

        if os.path.exists(temp_filepath):
            received += os.path.getsize(temp_filepath)
            if bar:
                bar.update_received(os.path.getsize(temp_filepath))
    else:
        open_mode = 'wb'

    if received < file_size:
        if faker:
            headers = fake_headers
        else:
            headers = {}
        if received:
            headers['Range'] = 'bytes=' + str(received) + '-'
        if refer:
            headers['Referer'] = refer

        response = request.urlopen(request.Request(url, headers = headers), None)
        try:
            range_start = int(response.headers['content-range'][6:].split('/')[0].split('-')[0])
            end_length = end = int(response.headers['content-range'][6:].split('/')[1])
            range_length = end_length - range_start
        except:
            content_length = response.headers['content-length']
            range_length = int(content_length) if content_length!=None else float('inf')

        if file_size != received + range_length:
            received = 0
            if bar:
                bar.received = 0
            open_mode = 'wb'

        with open(temp_filepath, open_mode) as output:
            while True:
                buffer = response.read(1024 * 256)
                if not buffer:
                    if received == file_size: # Download finished
                        break
                    else: # Unexpected termination. Retry request
                        headers['Range'] = 'bytes=' + str(received) + '-'
                        response = request.urlopen(request.Request(url, headers = headers), None)
                output.write(buffer)
                received += len(buffer)
                if bar:
                    bar.update_received(len(buffer))

    assert received == os.path.getsize(temp_filepath), '%s == %s == %s' % (received, os.path.getsize(temp_filepath), temp_filepath)

    if os.access(filepath, os.W_OK):
        os.remove(filepath) # on Windows rename could fail if destination filepath exists
    os.rename(temp_filepath, filepath)

def url_save_chunked(url, filepath, bar, refer = None, is_part = False, faker = False):
    if os.path.exists(filepath):
        if not force:
            if not is_part:
                if bar:
                    bar.done()
                print('Skipping %s: file already exists' % os.path.basename(filepath))
            else:
                if bar:
                    bar.update_received(os.path.getsize(filepath))
            return
        else:
            if not is_part:
                if bar:
                    bar.done()
                print('Overwriting %s' % os.path.basename(filepath), '...')
    elif not os.path.exists(os.path.dirname(filepath)):
        os.mkdir(os.path.dirname(filepath))

    temp_filepath = filepath + '.download'
    received = 0
    if not force:
        open_mode = 'ab'

        if os.path.exists(temp_filepath):
            received += os.path.getsize(temp_filepath)
            if bar:
                bar.update_received(os.path.getsize(temp_filepath))
    else:
        open_mode = 'wb'

    if faker:
        headers = fake_headers
    else:
        headers = {}
    if received:
        headers['Range'] = 'bytes=' + str(received) + '-'
    if refer:
        headers['Referer'] = refer

    response = request.urlopen(request.Request(url, headers = headers), None)

    with open(temp_filepath, open_mode) as output:
        while True:
            buffer = response.read(1024 * 256)
            if not buffer:
                break
            output.write(buffer)
            received += len(buffer)
            if bar:
                bar.update_received(len(buffer))

    assert received == os.path.getsize(temp_filepath), '%s == %s == %s' % (received, os.path.getsize(temp_filepath))

    if os.access(filepath, os.W_OK):
        os.remove(filepath) # on Windows rename could fail if destination filepath exists
    os.rename(temp_filepath, filepath)





def download_urls(urls, title, ext, total_size, output_dir='.', refer=None,  faker=False):
    assert urls
    if dry_run:
        print('Real URLs:\n%s' % '\n'.join(urls))
        return

    if player:
        launch_player(player, urls, total_size)
        return

    if not total_size:
        try:
            total_size = urls_size(urls)
        except:
            import traceback
            import sys
            traceback.print_exc(file = sys.stdout)
            pass

    title = get_filename(title)

    filename = '%s.%s' % (title, ext)
    filepath = os.path.join(output_dir, filename)
    if total_size:
        if not force and os.path.exists(filepath) and os.path.getsize(filepath) >= total_size * 0.9:
            print('Skipping %s: file already exists' % filepath)
            print()
            return
        bar = SimpleProgressBar(total_size, len(urls))
    else:
        bar = PiecesProgressBar(total_size, len(urls))

    if len(urls) == 1:
        url = urls[0]
        print('Downloading %s ...' % filename)
        url_save(url, filepath, bar, refer = refer, faker = faker)
        bar.done()
    else:
        parts = []
        print('Downloading %s.%s ...' % (title), ext)
        for i, url in enumerate(urls):
            filename = '%s[%02d].%s' % (title, i, ext)
            filepath = os.path.join(output_dir, filename)
            parts.append(filepath)
            bar.update_piece(i + 1)
            url_save(url, filepath, bar, refer = refer, is_part = True, faker = faker)
        bar.done()

    print()

def download_one_url(url, title, ext, index, output_dir='.', refer=None, faker=False):
    assert url
    if dry_run:
        print('Real URL [{}]:{}'.format(index, url))
        return

    if player:
        launch_player(player, [url],0)
        return


    title = get_filename(title)

    filename = '%s[%02d].%s' % (title, index, ext)
    filepath = os.path.join(output_dir, filename)

    print('Downloading %s ...' % filename)
    url_save(url, filepath, None, refer = refer, faker = faker)
    print()

def playlist_not_supported(name):
    def f(*args, **kwargs):
        raise NotImplementedError('Playlist is not supported for ' + name)
    return f

def print_info(site_info, title, type, size):
    if type:
        type = type.lower()
    if type in ['3gp']:
        type = 'video/3gpp'
    elif type in ['asf', 'wmv']:
        type = 'video/x-ms-asf'
    elif type in ['flv', 'f4v']:
        type = 'video/x-flv'
    elif type in ['mkv']:
        type = 'video/x-matroska'
    elif type in ['mp3']:
        type = 'audio/mpeg'
    elif type in ['mp4']:
        type = 'video/mp4'
    elif type in ['mov']:
        type = 'video/quicktime'
    elif type in ['ts']:
        type = 'video/MP2T'
    elif type in ['webm']:
        type = 'video/webm'

    if type in ['video/3gpp']:
        type_info = "3GPP multimedia file (%s)" % type
    elif type in ['video/x-flv', 'video/f4v']:
        type_info = "Flash video (%s)" % type
    elif type in ['video/mp4', 'video/x-m4v']:
        type_info = "MPEG-4 video (%s)" % type
    elif type in ['video/MP2T']:
        type_info = "MPEG-2 transport stream (%s)" % type
    elif type in ['video/webm']:
        type_info = "WebM video (%s)" % type
    #elif type in ['video/ogg']:
    #    type_info = "Ogg video (%s)" % type
    elif type in ['video/quicktime']:
        type_info = "QuickTime video (%s)" % type
    elif type in ['video/x-matroska']:
        type_info = "Matroska video (%s)" % type
    #elif type in ['video/x-ms-wmv']:
    #    type_info = "Windows Media video (%s)" % type
    elif type in ['video/x-ms-asf']:
        type_info = "Advanced Systems Format (%s)" % type
    #elif type in ['video/mpeg']:
    #    type_info = "MPEG video (%s)" % type
    elif type in ['audio/mp4']:
        type_info = "MPEG-4 audio (%s)" % type
    elif type in ['audio/mpeg']:
        type_info = "MP3 (%s)" % type
    else:
        type_info = "Unknown type (%s)" % type

    print("Video Site:", site_info)
    print("Title:     ", unescape_html(title))
    print("Type:      ", type_info)
    print("Size:      ", round(size / 1048576, 2), "MiB (" + str(size) + " Bytes)")
    print()

def mime_to_container(mime):
    mapping = {
        'video/3gpp': '3gp',
        'video/mp4': 'mp4',
        'video/webm': 'webm',
        'video/x-flv': 'flv',
    }
    if mime in mapping:
        return mapping[mime]
    else:
        return mime.split('/')[1]

def parse_host(host):
    """Parses host name and port number from a string.
    """
    if re.match(r'^(\d+)$', host) is not None:
        return ("0.0.0.0", int(host))
    if re.match(r'^(\w+)://', host) is None:
        host = "//" + host
    o = parse.urlparse(host)
    hostname = o.hostname or "0.0.0.0"
    port = o.port or 0
    return (hostname, port)

def set_proxy(proxy):
    proxy_handler = request.ProxyHandler({
        'http': '%s:%s' % proxy,
        'https': '%s:%s' % proxy,
    })
    opener = request.build_opener(proxy_handler)
    request.install_opener(opener)

def unset_proxy():
    proxy_handler = request.ProxyHandler({})
    opener = request.build_opener(proxy_handler)
    request.install_opener(opener)

# DEPRECATED in favor of set_proxy() and unset_proxy()
def set_http_proxy(proxy):
    if proxy == None: # Use system default setting
        proxy_support = request.ProxyHandler()
    elif proxy == '': # Don't use any proxy
        proxy_support = request.ProxyHandler({})
    else: # Use proxy
        proxy_support = request.ProxyHandler({'http': '%s' % proxy, 'https': '%s' % proxy})
    opener = request.build_opener(proxy_support)
    request.install_opener(opener)



def download_main(download, download_playlist, urls, playlist, **kwargs):
    for url in urls:
        if url.startswith('https://'):
            url = url[8:]
        if not url.startswith('http://'):
            url = 'http://' + url

        if playlist:
            download_playlist(url, **kwargs)
        else:
            download(url, **kwargs)

def script_main(script_name, download, download_playlist = None):
    version = 'You-Get %s, a video downloader.' % __version__
    help = 'Usage: %s [OPTION]... [URL]...\n' % script_name
    help += '''\nStartup options:
    -V | --version                           Display the version and exit.
    -h | --help                              Print this help and exit.
    '''
    help += '''\nDownload options (use with URLs):
    -f | --force                             Force overwriting existed files.
    -i | --info                              Display the information of videos without downloading.
    -u | --url                               Display the real URLs of videos without downloading.
    -c | --cookies                           Load NetScape's cookies.txt file.
    -F | --format <STREAM_ID>                Video format code.
    -o | --output-dir <PATH>                 Set the output directory for downloaded videos.
    -p | --player <PLAYER [options]>         Directly play the video with PLAYER like vlc/smplayer.
    -x | --http-proxy <HOST:PORT>            Use specific HTTP proxy for downloading.
    -y | --extractor-proxy <HOST:PORT>       Use specific HTTP proxy for extracting stream data.
         --no-proxy                          Don't use any proxy. (ignore $http_proxy)
         --debug                             Show traceback on KeyboardInterrupt.
    '''

    short_opts = 'Vhfiuc:nF:o:p:x:y:'
    opts = ['version', 'help', 'force', 'info', 'url', 'cookies', 'no-proxy', 'debug', 'format=', 'stream=', 'itag=', 'output-dir=', 'player=', 'http-proxy=', 'extractor-proxy=', 'lang=']
    if download_playlist:
        short_opts = 'l' + short_opts
        opts = ['playlist'] + opts

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_opts, opts)
    except getopt.GetoptError as err:
        log.e(err)
        log.e("try 'you-get --help' for more options")
        sys.exit(2)

    global force
    global dry_run
    global player
    global extractor_proxy
    global cookies_txt
    cookies_txt = None

    info_only = False
    playlist = False
    stream_id = None
    lang = None
    output_dir = '.'
    proxy = None
    extractor_proxy = None
    traceback = False
    for o, a in opts:
        if o in ('-V', '--version'):
            print(version)
            sys.exit()
        elif o in ('-h', '--help'):
            print(version)
            print(help)
            sys.exit()
        elif o in ('-f', '--force'):
            force = True
        elif o in ('-i', '--info'):
            info_only = True
        elif o in ('-u', '--url'):
            dry_run = True
        elif o in ('-c', '--cookies'):
            from http import cookiejar
            cookies_txt = cookiejar.MozillaCookieJar(a)
            cookies_txt.load()
        elif o in ('-l', '--playlist'):
            playlist = True
        elif o in ('--no-proxy',):
            proxy = ''
        elif o in ('--debug',):
            traceback = True
        elif o in ('-F', '--format', '--stream', '--itag'):
            stream_id = a
        elif o in ('-o', '--output-dir'):
            output_dir = a
        elif o in ('-p', '--player'):
            player = a
        elif o in ('-x', '--http-proxy'):
            proxy = a
        elif o in ('-y', '--extractor-proxy'):
            extractor_proxy = a
        elif o in ('--lang',):
            lang = a
        else:
            log.e("try 'you-get --help' for more options")
            sys.exit(2)
    if not args:
        print(help)
        sys.exit()

    set_http_proxy(proxy)

    try:
        if stream_id:
            if not extractor_proxy:
                download_main(download, download_playlist, args, playlist, stream_id=stream_id, output_dir=output_dir, info_only=info_only)
            else:
                download_main(download, download_playlist, args, playlist, stream_id=stream_id, extractor_proxy=extractor_proxy, output_dir=output_dir,  info_only=info_only)
        else:
            if not extractor_proxy:
                download_main(download, download_playlist, args, playlist, output_dir=output_dir,  info_only=info_only)
            else:
                download_main(download, download_playlist, args, playlist, extractor_proxy=extractor_proxy, output_dir=output_dir,  info_only=info_only)
    except KeyboardInterrupt:
        if traceback:
            raise
        else:
            sys.exit(1)
alias = {
        '163': 'netease',
        'fun': 'funshion',
        'iask': 'sina',
        'in': 'alive',
        'kankanews': 'bilibili',
        'smgbb': 'bilibili',
        'weibo': 'miaopai',
        '7gogo': 'nanagogo'
}
def url_to_module(url):
    video_host = r1(r'https?://([^/]+)/', url)
    video_url = r1(r'https?://[^/]+(.*)', url)
    assert video_host and video_url, 'invalid url: ' + url

    if video_host.endswith('.com.cn'):
        video_host = video_host[:-3]
    domain = r1(r'(\.[^.]+\.[^.]+)$', video_host) or video_host
    assert domain, 'unsupported url: ' + url

    k = r1(r'([^.]+)', domain)
    if k in alias.keys():
        k = alias[k]
    try:
        m = import_module('.'.join(['you_get','extractors', k]))
        return m ,url
    except(SyntaxError):
        log.wtf("SyntaxError in module {}".format(k))
    except:
        import http.client
        conn = http.client.HTTPConnection(video_host)
        conn.request("HEAD", video_url)
        res = conn.getresponse()
        location = res.getheader('location')
        if location is None:
            return import_module('you_get.extractors.generalembed'), url
        elif location != url:
            return url_to_module(location)
        else:
            raise ConnectionResetError(url)

def any_download(url, **kwargs):
    m, url = url_to_module(url)
    m.download(url, **kwargs)

def any_download_playlist(url, **kwargs):
    m, url = url_to_module(url)
    m.download_playlist(url, **kwargs)

def main():
    script_main('you-get', any_download, any_download_playlist)
