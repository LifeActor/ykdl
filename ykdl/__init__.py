#!/usr/bin/env python
# -*- coding: utf-8 -*

from .util.log import ColorHandler
import logging

logging.basicConfig(handlers=[ColorHandler()])
