import re


__all__ = ['match', 'match1', 'matchall']

def _format_str(pattern, string):
    '''Format the target which will be scanned, makes the worker happy.'''
    strtype = type(pattern)
    if not isinstance(string, strtype):
        try:
            string = strtype(string, 'utf-8')
        except TypeError:
            if isinstance(string, bytearray):
                string = bytes(string)
            else:
                for n in ('getvalue', 'tobytes', 'read', 'encode', 'decode'):
                    f = getattr(string, n, None)
                    if f:
                        try:
                            string = f()
                            break
                        except:
                            pass
                if not isinstance(string, (str, bytes)):
                    try:
                        if isinstance(string, int):  # defense memory burst
                            raise
                        string = strtype(string)
                    except:
                        string = str(string)
            if not isinstance(string, strtype):
                string = strtype(string, 'utf-8')
    return string

def match(obj, *patterns):
    '''Scans a object for matched some patterns with catch mode (matches first).

    Params:
        `obj`, any object which contains string data.
        `patterns`, arbitrary number of regex patterns.

    Returns all the catched substring of first match, or None.
    '''

    for pattern in patterns:
        string = _format_str(pattern, obj)
        match = re.search(pattern, string)
        groups = match and match.groups()
        if groups:
            return groups
    return None

def match1(obj, *patterns):
    '''Scans a object for matched some patterns with catch mode (catches first).

    Params: same as match()

    Returns the first catched substring, or None.
    '''

    groups = match(obj, *patterns)
    return groups and groups[0]


def matchall(obj, *patterns):
    '''Scans a object for matched some patterns with catch mode (matches all).

    Params: same as match()

    Returns a list of all the catched substring of matches, or a empty list.
    If a conformity form of catches in the list has be excepted, all the regex
    patterns MUST include a similar catch mode.
    '''

    ret = []
    for pattern in patterns:
        string = _format_str(pattern, obj)
        match = re.findall(pattern, string)
        ret += match

    return ret
