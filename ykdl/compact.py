import os
import sys
import io
import socket
import random
import logging
import tempfile
from socket import getaddrinfo as _getaddrinfo
from tempfile import NamedTemporaryFile as _NamedTemporaryFile

from .util.log import ColorHandler


logging.basicConfig(handlers=[ColorHandler()])


if os.name == 'nt':

    # Re-encoding Windows cmd shell output, py35 and below

    if sys.version_info < (3, 6):
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

    def NamedTemporaryFile(mode='w+b', buffering=-1, encoding=None, newline=None,
                           suffix=None, prefix='tmp', dir=None, delete=True,
                           *, errors=None):
        kwargs = vars()
        kwargs['delete'] = False  # skip setting O_TEMPORARY in the flags
        if sys.version_info < (3, 8):
            del kwargs['errors']
        tempfile = _NamedTemporaryFile(**kwargs)
        # at here setting whether is deleted on close
        tempfile._closer.delete = tempfile.delete = delete
        return tempfile

    tempfile._TemporaryFileCloser.close = _TemporaryFileCloser.close
    tempfile._TemporaryFileCloser.__del__ = _TemporaryFileCloser.__del__
    tempfile.NamedTemporaryFile = NamedTemporaryFile
    del _TemporaryFileCloser, NamedTemporaryFile


# Random getaddrinfo() result, it helps multi-connect to servers

def getaddrinfo(*args, **kwargs):
    addrlist = _getaddrinfo(*args, **kwargs)
    random.shuffle(addrlist)
    return addrlist

socket.getaddrinfo = getaddrinfo


#compact_dev_null = open(os.devnull, 'w')
