#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A HLS stream downloader that does not require ffmpeg
    Usage:
        download_hls(m3u8_url, name)

    Exception:
        UnsupportedError: This m3u8 format is currently not supported
        SegmentDownloadError: One of the segment is not able to be downloaded
        Mp4ConvertError: Cannot convert mpeg-ts file to mp4
'''

from __future__ import print_function

class UnsupportedError(Exception):
    pass

class SegmentDownloadError(Exception):
    pass

class Mp4ConvertError(Exception):
    pass


import re
import binascii
import os
import socket
import subprocess
import sys
from distutils.spawn import find_executable
from ykdl.compact import Request, urlopen, urljoin, compat_struct_pack
from ykdl.util.html import get_location, get_content, fake_headers
try:
    from Crypto.Cipher import AES
    can_decrypt_frag = True
except ImportError:
    can_decrypt_frag = False


def _can_decrypt(manifest):
    is_aes128_enc = '#EXT-X-KEY:METHOD=AES-128' in manifest
    return can_decrypt_frag or not is_aes128_enc

def _can_download(manifest):
    check_results = []
    check_results.append(not re.search(r'#EXT-X-KEY:METHOD=(?!NONE|AES-128)', manifest))
    is_aes128_enc = '#EXT-X-KEY:METHOD=AES-128' in manifest
    check_results.append(can_decrypt_frag or not is_aes128_enc)
    check_results.append(not (is_aes128_enc and r'#EXT-X-BYTERANGE' in manifest))
    return all(check_results)

def _parse_m3u8_attributes(attrib):
    info = {}
    for (key, val) in re.findall(r'(?P<key>[A-Z0-9-]+)=(?P<val>"[^"]+"|[^",]+)(?:,|$)', attrib):
        if val.startswith('"'):
            val = val[1:-1]
        info[key] = val
    return info

# Post processor
def _ffmpeg_available():
    return find_executable('ffmpeg') is not None

def _get_audio_codec(filename):
    cmd = ['ffmpeg', '-i', filename]
    try:
        handle = subprocess.Popen(
            cmd, stderr=subprocess.PIPE,
            stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        stdout_data, stderr_data = handle.communicate()
        if handle.wait() != 1:
            return None
    except (IOError, OSError):
        return None
    output = stderr_data.decode('ascii', 'ignore')
    match = re.search(
        r'Stream\s*#\d+:\d+(?:\[0x[0-9a-f]+\])?(?:\([a-z]{3}\))?:\s*Audio:\s*([0-9a-z]+)',
        output)
    if match:
        return match.group(1)
    return None

def _convert_ts_to_mp4(in_file, out_file):
    cmd = ['ffmpeg', '-y', '-i', in_file, '-c', 'copy', '-f', 'mp4']
    acodec = _get_audio_codec(in_file)
    print('[down_hls] Detected audio codec:', acodec)
    if acodec == 'aac':
        cmd += ['-bsf:a', 'aac_adtstoasc']
    cmd.append(out_file)
    handle = subprocess.Popen(
        cmd, stderr=subprocess.PIPE,
        stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = handle.communicate()
    if handle.wait() != 0:
        stderr = stderr.decode('utf-8', 'replace')
        msg = stderr.strip().split('\n')[-1]
        raise Mp4ConvertError(msg)


# Main function
def download_hls(m3u8_url, name):
    # Check if it is supported
    manifest = get_content(m3u8_url)
    if not _can_download(manifest):
        if not _can_decrypt(manifest):
            raise UnsupportedError('Please install PyCryto.')
        else:
            raise UnsupportedError('This HLS file is not supported. Consider using FFMpeg.')
    
    def is_ad_fragment_start(s):
        return (s.startswith('#ANVATO-SEGMENT-INFO') and 'type=ad' in s
            or s.startswith('#UPLYNK-SEGMENT') and s.endswith(',ad'))

    def is_ad_fragment_end(s):
        return (s.startswith('#ANVATO-SEGMENT-INFO') and 'type=master' in s
            or s.startswith('#UPLYNK-SEGMENT') and s.endswith(',segment'))
    
    # Get total number of fragments
    total_frags = 0
    ad_frags = 0
    ad_frag_next = False
    for line in manifest.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            if is_ad_fragment_start(line):
                ad_frag_next = True
            elif is_ad_fragment_end(line):
                ad_frag_next = False
            continue
        if ad_frag_next:
            ad_frags += 1
            continue
        total_frags += 1

    # retry times
    retry_times = 3

    # Set timeout to 10s.
    # If a segment cannot be downloaded within 10s, retry it.
    socket.setdefaulttimeout(10)

    # Scan manifest
    current_seg = 0
    frag_index = 0
    decrypt_info = {'METHOD': 'NONE'}
    byte_range = {}
    ad_frag_next = False
    headers = fake_headers.copy()

    ts_file = name + '.ts'
    with open(ts_file, 'wb') as f:
        for line in manifest.splitlines():
            line = line.strip()

            # Segment's URL
            if line:
                if not line.startswith('#'):
                    # Skip ad segment
                    if ad_frag_next:
                        continue
                    frag_index += 1
                    frag_url = (
                        line
                        if re.match(r'^https?://', line)
                        else urljoin(m3u8_url, line))

                    # Download segment
                    print('[down_hls] Download segments: (%i/%i)' % (frag_index, total_frags), end='\r')
                    sys.stdout.flush()
                    headers = fake_headers
                    if byte_range:
                        headers['Range'] = 'bytes=%d-%d' % (byte_range['start'], byte_range['end'])
                    else:
                        headers.pop('Range', None)
                    retry_count = 0
                    while retry_count < retry_times:
                        try:
                            req = Request(frag_url, headers=headers)
                            frag_content = urlopen(req).read()
                            break
                        except:
                            retry_count += 1
                            if retry_count < retry_times:
                                print('\n[down_hls] Download segment %i fails, retry...' % frag_index)
                    if retry_count == retry_times:
                        raise SegmentDownloadError('Download segment %i fails. Stop downloading.' % frag_index)

                    # Decrypt
                    if decrypt_info['METHOD'] == 'AES-128':
                        iv = decrypt_info.get('IV') or compat_struct_pack('>8xq', current_seg)
                        decrypt_info['KEY'] = decrypt_info.get('KEY') or get_content(decrypt_info['URI'])
                        frag_content = AES.new(
                            decrypt_info['KEY'], AES.MODE_CBC, iv).decrypt(frag_content)

                    # Write to file
                    f.write(frag_content)

                    current_seg += 1

                # Extract key
                elif line.startswith('#EXT-X-KEY'):
                    decrypt_url = decrypt_info.get('URI')
                    decrypt_info = _parse_m3u8_attributes(line[11:])
                    if decrypt_info['METHOD'] == 'AES-128':
                        if 'IV' in decrypt_info:
                            decrypt_info['IV'] = binascii.unhexlify(decrypt_info['IV'][2:].zfill(32))
                        if not re.match(r'^https?://', decrypt_info['URI']):
                            decrypt_info['URI'] = urljoin(
                                m3u8_url, decrypt_info['URI'])
                        if decrypt_url != decrypt_info['URI']:
                            decrypt_info['KEY'] = None
                
                # Correct seq number
                elif line.startswith('#EXT-X-MEDIA-SEQUENCE'):
                    current_seg = int(line[22:])

                # Get range
                elif line.startswith('#EXT-X-BYTERANGE'):
                    splitted_byte_range = line[17:].split('@')
                    sub_range_start = int(splitted_byte_range[1]) if len(splitted_byte_range) == 2 else byte_range['end']
                    byte_range = {
                        'start': sub_range_start,
                        'end': sub_range_start + int(splitted_byte_range[0]),
                    }

                # Skip ads
                elif is_ad_fragment_start(line):
                    ad_frag_next = True
                elif is_ad_fragment_end(line):
                    ad_frag_next = False

    # Convert ts file to mp4
    print()
    if not _ffmpeg_available():
        print('[down_hls] Please install ffmpeg to convert .ts file to mp4.')
        return
    print('[down_hls] Convert file to mp4...')
    mp4_file = name + '.mp4'
    _convert_ts_to_mp4(ts_file, mp4_file)
    os.remove(ts_file)
    print('[down_hls] Finished converting!')
