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
            sep = kwargs.get('sep', ' ')
            end = kwargs.get('end', '\n')
            stdout = sys.stdout
            file = kwargs.get('file') or stdout
            for arg in args:
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
                file.write(sep)
            file.write(end)
        __builtin__.print = print

    logging.root.addHandler(ColorHandler())
