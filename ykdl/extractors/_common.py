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
from ..util.kt_player import *

from ..util.lazy import lazy_import
lazy_import('from jsengine import JSEngine')
del lazy_import

import os
import sys
import re
import json
import time
import base64
import random
import functools
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
