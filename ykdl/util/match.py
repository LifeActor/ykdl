import re


__all__ = ['match', 'fullmatch', 'match1', 'matchm', 'matchall']

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
    '''Scans a object for matched some patterns with capture mode (matches first).

    Params:
        `obj`, any object which contains string data.
        `patterns`, arbitrary number of regex patterns.

    Returns the first Match object, or None.
    '''
    for pattern in patterns:
        string = _format_str(pattern, obj)
        m = re.search(pattern, string)
        if m:
            return m
    return None

def fullmatch(obj, *patterns):
    '''Scans a object for fully matched some patterns (matches first).

    Params: same as match()

    Returns the match string, or None.
    '''
    for pattern in patterns:
        string = _format_str(pattern, obj)
        m = re.fullmatch(pattern, string)
        if m:
            return m.string
    return None

def match1(obj, *patterns):
    '''Scans a object for matched some patterns with capture mode.

    Params: same as match()

    Returns the first captured substring, or None.
    '''
    m = match(obj, *patterns)
    return m and m.groups()[0]

def matchm(obj, *patterns):
    '''Scans a object for matched some patterns with capture mode.

    Params: same as match()

    Returns all captured substrings of the first Match object, or same number of
    None objects.
    '''
    m = match(obj, *patterns)
    return m and m.groups() or (None,) * re.compile(patterns[0]).groups


def matchall(obj, *patterns):
    '''Scans a object for matched some patterns with capture mode.

    Params: same as match()

    Returns a list of all the captured substring of matches, or a empty list.
    If a conformity form of captures in the list has be excepted, all the regex
    patterns MUST include a similar capture mode.
    '''
    ret = []
    for pattern in patterns:
        string = _format_str(pattern, obj)
        m = re.findall(pattern, string)
        ret += m

    return ret
