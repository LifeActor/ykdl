#!/usr/bin/env python
# -*- coding: utf-8 -*

from .util.log import ColorHandler
import logging

import sys

if sys.version_info[0] == 3:
   logging.basicConfig(handlers=[ColorHandler()])
else:
   logging.root.addHandler(ColorHandler())
