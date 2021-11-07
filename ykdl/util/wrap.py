'''Wrap the functions of official packages which have been frequent used.'''

import pkgutil
import hashlib

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

    For example:

        >>> hash.md5('1234567890')
        'e807f1fcf82d132f9bb018ca6738a19f'
    '''

    def __getattr__(self, name):
        alg = getattr(hashlib, name)

        def hash(*args, **kwargs):
            if args:
                data, *args = args  # if len(args) > 2, raise in finally line
            else:
                # there are two names of first param 
                data = kwargs.pop('string', None) or kwargs.pop('data', b'')
            if hasattr(data, 'encode'):
                data = data.encode()
            if name.lower().startswith ('shake_'):
                digest_size = kwargs.pop('digest_size', None)
                if digest_size is None:
                    raise ValueError('digest_size is needed for shake.')
                return alg(data, *args, **kwargs).hexdigest(digest_size)
            else:
                return alg(data, *args, **kwargs).hexdigest()

        hash.__doc__ = '''
            Return the resoult of a new hashing object {name}().hexdigest().

            Params: same as hashlib.{name}(), but string/data can be a str.
            '''.format(name=name)
        return hash

hash = HASH()
del HASH
