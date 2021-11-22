from .match import match, match1


__all__ = ['human_size', 'human_time', 'format_vps']

def _format_str(s):
    if isinstance(s, bytes):
        s = s.decode()
    s = s.lower()
    n = match1(s, '^((?:0x)?[0-9a-f])$')
    if n and match(n, '([a-fx])'):
        return s.replace(n, str(int(n, 16)))
    return s

_size_units = {
    None: 1,
     'k': 1 << 10,
     'm': 1 << 20,
     'g': 1 << 30,
     't': 1 << 40
}

def human_size(n, unit=None):
    '''Convert giving number to a hunman read size with unit.

    Params:
        `n`, integer,
             integer and scientific notation string with or without a unit,
             float string with a unit,
             hex string without a unit.
        `unit`, specify the unit, base unit "Bytes" is not optional.
    '''
    if isinstance(n, (str, bytes)):
        n = _format_str(n)
        try:
            n, nu = match(n, '''(?x)
                             (?:
                                 ^          |  # start
                                 \De        |  # no scientific notation
                                 [^\-\.\de]    # no negative, dot, number
                             )
                             (
                                 \d+           # integer
                                 (?:\.\d+)?    # float
                                 (?!\.)        # bad float
                                 (?:e\d+)?     # scientific notation
                                 (?![\.\de])   # bad scientific notation
                             )
                             \s*
                             (?:([kmgt])i?b)?  # unit
                             ''')
        except TypeError:
            raise ValueError('invalid literal for human_size(): %r' % n)
        f = float(n)
        if not nu and f % 1:
            raise ValueError(
                    'float number in string MUST be provided with a unit')
        f = f * _size_units[nu]
        n = int(f)
        if f > n:
            n += 1
    elif not isinstance(n, int):
        raise TypeError('argument must be a string, a bytes object '
                        'or a integer number, not %r' % type(n))
    if n < 0:
        return 'N/A'
    n = float(n)
    unit = unit and match1(unit.lower(), '([kmgt])i?b')
    u = _size_units.get(unit)
    if u:
        n /= u
        unit = unit.upper() + 'iB'
    else:
        for unit in ('Bytes', 'KiB', 'MiB', 'GiB', 'TiB'):
            if unit != 'TiB' and n >= 1024:
                n /= 1024
            else:
                break
    return ' '.join(['{:.3f}'.format(n).rstrip('0').rstrip('.'), unit])

def human_time(t, days=False):
    '''Convert giving number to a hunman read timestamp.

    Params:
        `days`, wethere to show days or not.
    '''
    if isinstance(t, (str, bytes)):
        t = _format_str(t)
    if not isinstance(t, int):
        t = int(t)
    if t < 0:
        return 'N/A'
    pt = t,
    for _ in range(2):
        if pt[0]:
            pt = divmod(pt[0], 60) + pt[1:]
    if days and len(pt) == 3 and pt[0] >= 24:
        days, pt0 = divmod(pt[0], 24)
        return '{}d {:02d}:{:02d}:{:02d}'.format(days, pt0, *pt[1:])
    return ':'.join('%02d' % t for t in pt)

def format_vps(*wh):
    '''Convert giving width and height to stream ID and progressive scan marking.

    e.g.
        1920, 1080      => 'BD', '1080P'
        '720x540'       => 'HD', '540P'
        '540', '960'    => 'HD', '540P'
    '''
    if len(wh) == 1 and isinstance(wh[0], str):
        wh = wh[0].lower().split('x')
    assert len(wh) == 2, 'need width and height.'
    def get_n(n):
        try:
            return int(n)
        except ValueError:
            return int(n[:-1])
    wh = list(map(get_n, wh))
    max_ps, min_ps = max(wh), min(wh)
    ps = abs(max_ps / min_ps * 3 - 4) < 0.5 and max_ps * 4 / 3 or max_ps
    if ps <= 480:
        id = 'LD'
    elif ps <= 640:
        id = 'SD'
    elif ps <= 960:
        id = 'HD'
    elif ps <= 1280:
        id = 'TD'
    elif ps <= 1920:
        id = 'BD'
    elif ps <= 2560:
        id = '2K'
    else:
        id = '{:.1f}'.format(ps/1000).rstrip('0').rstrip('.') + 'K'
    return id, str(min_ps) + 'P'

_stream_index = 'OG', '*K', 'BD', 'TD', 'HD', 'SD', 'LD'

def stream_index(id):
    '''Used by videoinfo.VideoInfo.sort().'''
    if id.isdecimal():
        return -int(id)  # m3u8 bandwidth
    id = id.upper()
    i = 0
    if id.endswith('K'):  # 3.5K
        i += float(id[:-1]) * 0.01
        id = '*K'
    elif len(id) > 2 and id.startswith('BD'):  # BD4M
        i += float(id[2:-1]) * 0.01
        id = 'BD'
    try:
        return _stream_index.index(id) - i
    except ValueError:
        return id
