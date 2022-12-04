# -*- coding: utf-8 -*-

import sys
import platform
from .wrap import hash


if sys.platform.startswith(('msys', 'cygwin')):
    system = 'Windows'
else:
    system = platform.system()

translate_table = None
translate_table_cs = None

def _ensure_translate_table():
    global translate_table, translate_table_cs
    if translate_table is None:
        ### Visible ###
        # Control characters
        # Delete them except Tab and Newline
        translate_table = dict.fromkeys((*range(0x20), *range(0x7F, 0xA0)))
        translate_table.update({
            ord('\t'): ' ',
            ord('\n'): '-',
        })

        # Unicode Category Separator characters
        # Convert to Space
        translate_table.update(dict.fromkeys((
            # Generate:
            #   import sys
            #   from unicodedata import category 
            #   ', '.join((f'0x{u:X}'
            #              for u in range(0x20, sys.maxunicode)
            #              if category(chr(u))[0] == 'Z'))
            0x20, 0xA0,
            0x1680, 0x2000, 0x2001, 0x2002, 0x2003, 0x2004,
            0x2005, 0x2006, 0x2007, 0x2008, 0x2009, 0x200A,
            0x2028, 0x2029, 0x202F, 0x205F, 0x3000
        ), ' '))

        translate_table_cs = translate_table.copy()

        ### Legality ###
        translate_table.update({
            ord('/'): '／',  # File path component separator
        })
        if system == 'Windows':
            # FAT12 / FAT16 / FAT32 (VFAT LFNs)
            # exFAT
            # NTFS / ReFS (Win32 namespace)
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
            # HFS+ except longstanding cases
            if int(platform.release().split('.')[0]) < 17:
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

    result = text[:trim]
    overflow = text[trim:]
    if overflow:
        crc = hash.crc32(overflow)
        result += '_{crc}'.format(**vars())
    return result

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
