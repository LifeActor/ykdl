#!/usr/bin/env python
# -*- coding: utf-8 -*

from __future__ import print_function
from .util.log import ColorHandler
import logging

import sys

if sys.version_info[0] == 3:
    if sys.platform.startswith('win') and sys.version_info[1] < 6:
        import io
        # hack sys.stdout in Windows cmd shell
        sys.stdout = io.TextIOWrapper(sys.stdout.detach(),
                                      encoding=sys.stdout.encoding,
                                      errors='ignore')

    logging.basicConfig(handlers=[ColorHandler()])
else:
    if sys.platform.startswith('win'):
        import __builtin__
        # hack print function in Windows cmd shell
        def print(*args, **kwargs):
            sep = kwargs.get('sep')
            if sep is None:
                sep = ' '
            elif not isinstance(sep, (str, unicode)):
                raise TypeError('sep must be None, str or unicode, not ' +
                                str(type(sep)).split("'")[1])
            end = kwargs.get('end')
            if end is None:
                end = '\n'
            elif not isinstance(end, (str, unicode)):
                raise TypeError('end must be None, str or unicode, not ' +
                                str(type(sep)).split("'")[1])
            stdout = sys.stdout
            file = kwargs.get('file')
            if file is None:
                file = stdout
            l = len(args)
            for i in xrange(l):
                arg = args[i]
                if isinstance(arg, str):
                    pass
                elif isinstance(arg, unicode):
                    if file is stdout:
                        arg = arg.encode(file.encoding, 'ignore')
                    else:
                        arg = arg.encode(file.encoding)
                else:
                    arg = str(arg)
                file.write(arg)
                if i + 1 < l:
                    file.write(sep)
            file.write(end)
        __builtin__.print = print

    logging.root.addHandler(ColorHandler())
