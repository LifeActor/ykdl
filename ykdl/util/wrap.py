'''Wrap the functions of official packages which have been frequent used.'''

import os
import ast
import sys
import json
import zlib
import base64
import random
import string
import pkgutil
import traceback


__all__ = ['reverse_list_dict', 'b64', 'unb64', 'hash', 'literalize',
           'deprecated', 'get_pkgdata_str', 'get_pkgdata_bytes',
           'get_random_hex', 'get_random_str', 'get_random_name',
           'get_random_id', 'get_random_uuid', 'get_random_uuid_hex']

def reverse_list_dict(d):
    '''Reverse {key: values[List]} to {value: key}'''
    return dict(sum([[(v, k) for v in vs] for k, vs in d.items()], []))

def b64(s, target=str, urlsafe=False):
    '''Encode string/bytes-like object to Base64.

    Params:
        `target` is `str` or `bytes`
        `urlsafe` to use `urlsafe_b64encode`
    '''
    encode = getattr(base64, urlsafe and 'urlsafe_b64encode' or 'b64encode')
    if isinstance(s, str):
        s = s.encode()
    if target is str:
        return encode(s).decode()
    if target is bytes:
        return encode(s)

def unb64(b64, target=str, urlsafe=False):
    '''Decode Base64 object to string/bytes.

    Params:
        `target` is `str` or `bytes`
        `urlsafe` to use `urlsafe_b64decode`
    '''
    decode = getattr(base64, urlsafe and 'urlsafe_b64decode' or 'b64decode')
    if target is str:
        return decode(b64).decode()
    if target is bytes:
        return decode(b64)

def get_pkgdata_str(package, resource, url=None, encoding=None):
    '''Fetch the resource data from package, or from a fallback URL if give.

    Params: `package` package name usually the `__name__` attribute with
            current module.

            `resource` the file name of resource.

            `url` the fallback URL, optional.

            `encoding` use for decode, optional.

    Return: str or bytes (call from get_pkgdata_bytes()) of requested resource.
    '''
    try:
        data = pkgutil.get_data(package, resource)
    except IOError:
        if not url:
            raise
        return get_content(url, encoding=encoding)
    else:
        if encoding != 'ignore':
            data = data.decode(encoding or 'utf-8')
        return data

def get_pkgdata_bytes(package, resource, url=None):
    '''Fetch the resource data from package, or from a fallback URL if give.
    
    Params: same as get_pkgdata_str(), but encoding could not be set, it's
            always 'ignore'.

    Return: bytes of requested resource.
    '''
    return get_pkgdata_str(package, resource, url, 'ignore')

class HASH:
    '''Supported hash algorithm constructors are provided via attribute name,
    just likes hashlib, but only return hex digest.
    And the object is also compatible with built-in function `hash`.

    For example:

        >>> hash.md5('1234567890')
        'e807f1fcf82d132f9bb018ca6738a19f'
        >>> hash(1.0)
        1

    ----------------------------------------------------------------------'''

    algorithms_available = {'MD5', 'SHA1', 'SHA224', 'SHA256', 'SHA384', 'SHA512'}
    init = None

    def __getattr__(self, name):
        import hashlib
        if self.init is None:
            self.algorithms_available |= hashlib.algorithms_available
            self.__class__.init = True
        if name not in self.algorithms_available:
            raise AttributeError('%r object has no attribute: '
                                 'unsupported hash type %r'
                                 % (self.__class__.__name__, name))

        def hash(*args, **kwargs):
            if args:
                data, *args = args
                # if len(args) > 0, raise in finally line
            else:
                # there are two names of first parameter
                data = kwargs.pop('string', None) or kwargs.pop('data', b'')
            if hasattr(data, 'encode'):
                data = data.encode()
            args = name, data, *args
            if name.lower().startswith ('shake_'):
                digest_size = kwargs.pop('digest_size', None)
                if digest_size is None:
                    raise ValueError('digest_size is needed for shake.')
                return hashlib.new(*args, **kwargs).hexdigest(digest_size)
            else:
                return hashlib.new(*args, **kwargs).hexdigest()

        hash.__doc__ = '''
            Return the resoult of a new hashing object {name}().hexdigest().

            Params: same as hashlib.{name}(), but string/data can be a str.
            '''.format(name=name)
        return hash

    @staticmethod
    def crc32(data):
        '''Return the CRC-32 hexdigest of data.

        `data`: string or bytes-like object
        '''
        if hasattr(data, 'encode'):
            data = data.encode()
        return '{:0>8x}'.format(zlib.crc32(data))

    def __call__(self, obj):
        return _hash(obj)

_hash = hash
hash = HASH()
del HASH

def literalize(s, JSON=False):
    '''Literalize the giving string as a Python/JSON literal.'''
    if JSON:
        return json.loads('"{}"'.format(s))
    else:
        return ast.literal_eval('"""{}"""'.format(s))

_deprecated_once = set()

def deprecated(msg):
    '''Forced deprecated warning.'''
    f = sys._getframe(2)
    key = msg, f.f_code.co_filename, f.f_lineno
    if key in _deprecated_once:
        return
    _deprecated_once.add(key)
    print('DeprecationWarning: ', msg, '\n', *traceback.format_stack(f),
          sep='', file=sys.stderr)

_id_cache = {}
_ascii_letters_digits = string.ascii_letters + string.digits

def get_random_hex(l):
    '''Return a random hex string with specified length.'''
    l, r = divmod(l, 2)
    if r:
        raise ValueError('the length of hex string MUST be a even number')
    return os.urandom(l).hex()

def get_random_str(l):
    '''Return a random string with specified length, the population includes
    a-z, A-Z, 0-9.
    '''
    return ''.join(random.choices(_ascii_letters_digits, k=l))

def get_random_name(l):
    '''Return a random string with specified length that can be used as a
    variables/constants name.
    '''
    return random.choice(string.ascii_lowercase) + get_random_str(l - 1)

def get_random_id(l, name=None):
    '''Return a random lowercase string with specified length that can be used
    as a unique identifier, the name is use to keeping persistenc.
    '''
    if name is None:
        return get_random_str(l).lower()
    try:
        return _id_cache[(name, l)]
    except KeyError:
        _id_cache[(name, l)] = id = get_random_str(l).lower()
        return id

def get_random_uuid(name=None):
    '''Return a random UUID string with style version 4, the name is use to
    keeping persistenc.
    '''
    import uuid
    if name is None:
        return str(uuid.uuid4())
    try:
        return _id_cache[(name, 'uuid')]
    except KeyError:
        _id_cache[(name, 'uuid')] = id = str(uuid.uuid4())
        return id

def get_random_uuid_hex(name=None):
    '''Return a random UUID hex string with style version 4, the name is use to
    keeping persistenc.
    '''
    import uuid
    if name is None:
        return uuid.uuid4().hex
    return get_random_uuid(name).replace('-', '')
