# -*- coding: utf-8 -*-

import sys
import platform


if sys.platform.startswith(('msys', 'cygwin')):
    system = 'Windows'
else:
    system = platform.system()

translate_table = None

def legitimize(text, compress='. -_', strip='. -_', trim=82):
    '''Converts a string to a valid filename.'''

    global translate_table

    if translate_table is None:
        # Non-Printable Characters
        # POSIX systems could accept 1-31, but we wouldn't like this
        # Delete them except tab and newline
        translate_table = dict.fromkeys(range(32))
        translate_table.update({
            ord('\t'): ' ',
            ord('\n'): '-',
            ord('/'): '／',
        })
        if system == 'Windows':
            # Windows (non-POSIX namespace), drop old reserved characters
            translate_table.update({
                ord('\\'): '＼',
                ord(':'): '：',
                ord('*'): '＊',
                ord('?'): '？',
                ord('"'): '＂',
                ord('<'): '＜',
                ord('>'): '＞',
                ord('|'): '｜',
            })
        elif system == 'Darwin':
            # Mac OS HFS+
            translate_table.update({
                ord(':'): '：',
            })

    text = text.translate(translate_table)

    # Compress same characters, default target are dot, space, minus and underline
    compress = set(list(compress))
    chars = []
    last_char = None
    for char in text:
        if not (char is last_char and char in compress):
            chars.append(char)
        last_char = char
    text = ''.join(chars)


    # Strip characters, default target are same as compress default target
    text = text.strip(strip)

    # Trim to specifying Unicode characters length, default target is 82
    return text[:trim]
