# -*- coding: utf-8 -*-

import sys
import zlib
import platform
from unicodedata import category


if sys.platform.startswith(('msys', 'cygwin')):
    system = 'Windows'
else:
    system = platform.system()

translate_table = None
translate_table_cs = None

def _ensure_translate_table():
    global translate_table, translate_table_cs
    if translate_table is None:
        # Control characters
        # Delete them except Tab and Newline
        translate_table = dict.fromkeys((*range(32), *range(127, 160)))
        translate_table.update({
            ord('\t'): ' ',
            ord('\n'): '-',
        })

        # Unicode Category Separator characters
        # Convert to Space
        translate_table.update({
            u: ' '
            for u in range(32, sys.maxunicode)
            if category(chr(u))[0] == 'Z'
        })

        translate_table_cs = translate_table.copy()

        # Legitimize characters for filename
        translate_table.update({
            ord('/'): '／',  # File path component separator
        })
        if system == 'Windows':
            # Windows NTFS (Win32 namespace)
            translate_table.update({
                ord('\\'): '＼',
                ord(':'): '꞉',
                ord('*'): '∗',
                ord('?'): '‽',
                ord('"'): '″',
                ord('<'): '＜',
                ord('>'): '＞',
                ord('|'): '¦',
            })
        elif system == 'Darwin':
            # Mac OS HFS+
            translate_table.update({
                ord(':'): '꞉',
            })

def legitimize(text, compress='', strip='', trim=82):
    '''Converts a string to a valid filename.
    Also see `help(compress_strip)`.
    '''
    _ensure_translate_table()
    text = text.translate(translate_table)
    text = compress_strip(text, compress, strip, True)

    assert text, 'the given filename could not be legalized!'

    crc = zlib.crc32(text[trim:].encode())
    if crc:
        crc = '{crc:x}'.format(**vars())
    return text[:trim], crc

def compress_strip(text, compress='', strip='', translated=False):
    '''Compress same characters, and then strip.
    Dot, Minus, Underline and whole characters of Unicode Category Separator
    will always be compressed and stripped.
    '''
    if not translated:
        _ensure_translate_table()
        text = text.translate(translate_table_cs)

    compress = set(c for c in compress + '.-_ ')
    chars = []
    last_char = None
    for char in text:
        if not (char is last_char and char in compress):
            chars.append(char)
        last_char = char
    return ''.join(chars).strip(strip + '.-_ ')
