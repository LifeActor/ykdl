import re


__all__ = ['match', 'match1', 'matchall']

def _format_str(pattern, text):
    strtype = type(pattern)
    if not isinstance(text, strtype):
        try:
            text = strtype(text, 'utf-8')
        except TypeError:
            if hasattr(text, 'decode'):
                if strtype is str:
                    text = text.decode()
            else:
                text = str(text)
            if strtype is bytes and hasattr(text, 'encode'):
                text = text.encode()
    return text

def match(text, *patterns):
    """Scans through a string for substrings matched some patterns (first groups only).

    Args:
        text: A string to be scanned.
        patterns: Arbitrary number of regex patterns.

    Returns:
        When matches, returns first match groups.
        When no matches, return None
    """

    for pattern in patterns:
        text = _format_str(pattern, text)
        match = re.search(pattern, text)
        groups = match and match.groups()
        if groups:
            return groups
    return None

def match1(text, *patterns):
    """Scans through a string for substrings matched some patterns (first-subgroups only).

    Args:
        text: A string to be scanned.
        patterns: Arbitrary number of regex patterns.

    Returns:
        When matches, returns first-subgroups from first match.
        When no matches, return None
    """

    groups = match(text, *patterns)
    return groups and groups[0]


def matchall(text, *patterns):
    """Scans through a string for substrings matched some patterns.

    Args:
        text: A string to be scanned.
        patterns: a list of regex pattern.

    Returns:
        a list if matched. empty if not.
    """

    ret = []
    for pattern in patterns:
        text = _format_str(pattern, text)
        match = re.findall(pattern, text)
        ret += match

    return ret
