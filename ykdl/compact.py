import os
import sys
import io
import socket
import random
import inspect
import logging
import tempfile
import builtins
import functools

from .util.log import ColorHandler


logging.basicConfig(handlers=[ColorHandler()])


builtins.Infinity = float('inf')


try:
    functools.cache
except AttributeError:
    exec('''\
def cache(user_function, /):
    'Simple lightweight unbounded cache.  Sometimes called "memoize".'
    return lru_cache(maxsize=None)(user_function)
''', functools.__dict__)


if sys.version_info < (3, 10):
    import types
    types.NoneType = type(None)


def bound_monkey_patch(orig, new):
    '''Monkey patch the original function with new, and bind the original
    function as its first argument, at end clear the new function from the
    module which it defined with.
    '''
    if hasattr(orig, 'orig'):
        raise ValueError(
                'Monkey patched function can not be patched twice, please use '
                'the attribute `orig` to get original function and patch it.')
    f = sys._getframe()
    module = f.f_globals['__name__']
    co_name = f.f_code.co_name
    argspec = str(inspect.signature(orig))
    marks = '*' * 76
    doc = new.__doc__ or ''
    doc += '''
    {marks}
    {orig.__name__}.orig{argspec}

    This is a bound monkey patched function via use '{module}.{co_name}',
    {orig.__name__}.orig is the original.
    '''
    if orig.__doc__:
        doc += '''{marks}

    {orig.__doc__}
    '''
    new.__doc__ = doc.format(**vars())
    new.orig = orig
    new = new.__get__(orig, type(new))  # bind original as the first argument
    orig.__globals__[orig.__name__] = new
    del new.__globals__[new.__name__]


if os.name == 'nt':

    # Re-encoding Windows cmd shell output, py35 and below

    if sys.version_info < (3, 6):
        sys.stderr = io.TextIOWrapper(sys.stderr.detach(),
                                      encoding=sys.stderr.encoding,
                                      errors='ignore',
                                      line_buffering=True)
        sys.stdout = io.TextIOWrapper(sys.stdout.detach(),
                                      encoding=sys.stdout.encoding,
                                      errors='ignore',
                                      line_buffering=True)


    # Implements as general method instead of Windows primitive delete-on-close
    # which would lock the temporary files

    class _TemporaryFileCloser:
        # codes were copied from tempfile._TemporaryFileCloser
        def close(self, unlink=os.unlink):
            if not self.close_called and self.file is not None:
                self.close_called = True
                try:
                    self.file.close()
                finally:
                    if self.delete:
                        unlink(self.name)
        def __del__(self):
            self.close()

    def NamedTemporaryFile(orig,
                           mode='w+b', buffering=-1, encoding=None, newline=None,
                           suffix=None, prefix='tmp', dir=None, delete=True,
                           *, errors=None):
        '''Windows delete-on-close flag will not be used, a closer is use to
        close the temporary file, so it can be opened as shared.
        '''
        kwargs = vars()
        del kwargs['orig']
        kwargs['delete'] = False  # skip setting os.O_TEMPORARY in the flags
        if sys.version_info < (3, 8):
            del kwargs['errors']
        tempfile = orig(**kwargs)
        # at here setting whether is deleted on close
        tempfile._closer.delete = tempfile.delete = delete
        return tempfile

    tempfile._TemporaryFileCloser.close = _TemporaryFileCloser.close
    tempfile._TemporaryFileCloser.__del__ = _TemporaryFileCloser.__del__
    del _TemporaryFileCloser
    bound_monkey_patch(tempfile.NamedTemporaryFile, NamedTemporaryFile)


# Shuffles getaddrinfo() result, that helps multi-connect to servers

def getaddrinfo(orig, *args, **kwargs):
    '''Shuffles the orig result.'''
    addrlist = orig(*args, **kwargs)
    random.shuffle(addrlist)
    return addrlist

bound_monkey_patch(socket.getaddrinfo, getaddrinfo)


#compact_dev_null = open(os.devnull, 'w')
