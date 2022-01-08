'''How we do import here.

We do import the most functions/classes and variables/constants which are
common using in our extractors at here.

Don't import ALL (*) from module unless ensure all them are needed, if not sure
then only import the module or its attributes which we are used.
'''

from ..extractor import *
from ..mediainfo import MediaInfo

from ..util.http import *
from ..util.human import *
from ..util.m3u8 import *
from ..util.match import *
from ..util.wrap import *

import os
import sys
import re
import json
import time
import base64
import random
import urllib.parse
import urllib.request

from html import *
from urllib.parse import *
from tempfile import NamedTemporaryFile

g = globals()
for name in urllib.request.__all__:
    if name.startswith('HTTP') or name.endswith('Handler'):
        g[name] = urllib.request.__dict__[name]
del g, name


def lazy_import(importstr):

    assert importstr.startswith(('import ', 'from ')), \
           ImportError('Wrong lazy import string: %r' % importstr)

    class lazy_obj:
        def __bool__(self):
            return bool(self.__obj)
        def __call__(self, *args, **kwargs):
            return self.__obj(*args, **kwargs)
        def __getattribute__(self, name):
            nonlocal obj
            if obj is obj_none:
                try:
                    exec(importstr)
                except ImportError:
                    obj = None
                else:
                    obj = locals()[obj_name]
            if name == '_lazy_obj__obj':
                return obj
            return getattr(obj, name)

    obj = obj_none = object()
    obj_name = importstr.split()[-1].split('.')[0]
    globals()[obj_name] = lazy_obj()

lazy_import('from jsengine import JSEngine')
del lazy_import
