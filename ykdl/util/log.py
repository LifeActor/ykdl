import os, sys

IS_ANSI_TERMINAL = os.getenv('TERM', '').startswith((
    'eterm-color',
    'linux',
    'screen',
    'vt100',
    'xterm'
))

if not IS_ANSI_TERMINAL and os.name == 'nt':
    try:
        import colorama
    except ImportError:
        pass
    else:
        colorama.init()
        IS_ANSI_TERMINAL = True

# ANSI escape code
# REF: https://en.wikipedia.org/wiki/ANSI_escape_code
RESET = 0
BOLD = 1
UNDERLINE = 4
NEGATIVE = 7
NO_BOLD = 21
NO_UNDERLINE = 24
POSITIVE = 27
BLACK = 30
RED = 31
GREEN = 32
YELLOW = 33
BLUE = 34
MAGENTA = 35
CYAN = 36
LIGHT_GRAY = 37
DEFAULT = 39
BLACK_BACKGROUND = 40
RED_BACKGROUND = 41
GREEN_BACKGROUND = 42
YELLOW_BACKGROUND = 43
BLUE_BACKGROUND = 44
MAGENTA_BACKGROUND = 45
CYAN_BACKGROUND = 46
LIGHT_GRAY_BACKGROUND = 47
DEFAULT_BACKGROUND = 49
DARK_GRAY = 90                 # xterm
LIGHT_RED = 91                 # xterm
LIGHT_GREEN = 92               # xterm
LIGHT_YELLOW = 93              # xterm
LIGHT_BLUE = 94                # xterm
LIGHT_MAGENTA = 95             # xterm
LIGHT_CYAN = 96                # xterm
WHITE = 97                     # xterm
DARK_GRAY_BACKGROUND = 100     # xterm
LIGHT_RED_BACKGROUND = 101     # xterm
LIGHT_GREEN_BACKGROUND = 102   # xterm
LIGHT_YELLOW_BACKGROUND = 103  # xterm
LIGHT_BLUE_BACKGROUND = 104    # xterm
LIGHT_MAGENTA_BACKGROUND = 105 # xterm
LIGHT_CYAN_BACKGROUND = 106    # xterm
WHITE_BACKGROUND = 107         # xterm

def sprint(text, *colors):
    '''Format text with color or other effects into ANSI escaped string.'''
    if IS_ANSI_TERMINAL and colors:
        color = ';'.join(map(str, colors))
        return '\33[{color}m{text}\33[0m'.format(**vars())
    return text

import logging

_LOG_COLOR_MAP_ = {
    logging.CRITICAL : '31;1',
    logging.ERROR    : RED,
    logging.WARNING  : YELLOW,
    logging.INFO     : LIGHT_GRAY,
    logging.DEBUG    : GREEN,
    logging.NOTSET   : DEFAULT
}

_colorFormatter = logging.Formatter('\33[%(color)sm%(levelname)s:%(name)s:%(message)s\33[0m')

class ColorHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)
        if IS_ANSI_TERMINAL:
            self.formatter = _colorFormatter

    def format(self, recode):
        if IS_ANSI_TERMINAL:
            recode.color = _LOG_COLOR_MAP_[recode.levelno]
        return logging.StreamHandler.format(self, recode)
