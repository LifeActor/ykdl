'''How we do import here.

We do import the most functions/classes and variables/constants which are
common using in our extractors at here.

Don't import ALL (*) from module unless ensure all them are needed, if not sure
then only import the module or its attributes which we are used.
'''

from ..embedextractor import EmbedExtractor
from ..extractor import VideoExtractor
from ..simpleextractor import SimpleExtractor
from ..videoinfo import VideoInfo

from ..util.http import *
from ..util.human import *
from ..util.jsengine import JSEngine
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
