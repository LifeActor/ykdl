'''Some simple functions use for lazy loading.'''

import sys
from ctypes import pythonapi, py_object, c_int


__all__ = ['proxy', 'lazy_import']


def create_attr_code():
    OP = '''
def __{}__(self, other):
    return self.__wrapped__ {} other
'''.format
    ROP = '''
def __r{}__(self, other):
    return other {} self.__wrapped__
'''.format
    IOP = '''
def __i{}__(self, other):
    self.__wrapped__ {}= other
'''.format
    OPF = '''
def __{}__(self):
    return {} self.__wrapped__
'''.format
    OPC = '''
def __{}__(self):
    return {}(self.__wrapped__)
'''.format

    operations = {
        'lt': '<',
        'le': '<=',
        'eq': '==',
        'ne': '!=',
        'ge': '>=',
        'gt': '>',
  'contains': 'in',
    }
    operations_x = {
        'add': '+',
        'sub': '-',
        'mul': '*',
    'truediv': '/',
        'pow': '**',
        'mod': '%',
   'floordiv': '//',
        'and': '&',
         'or': '|',
        'xor': '^',
     'lshift': '<<',
     'rshift': '>>',
     'matmul': '@',
     'concat': '+',
    }
    operations_f = {
        'inv': '~',
     'invert': '~',
        'pos': '+',
        'neg': '-',
    }
    operations_c = [
        'abs',
       'bool',
      'bytes',
        'dir',
     'divmod',
      'float',
       'hash',
        'hex',
        'int',
       'iter',
        'len',
       'next',
        'oct',
   'reversed',
      'round',
        'str',
    ]
    code = []

    for operation, operator in operations.items():
        code.append(OP(operation, operator))

    for operation, operator in operations_x.items():
        code.append(OP(operation, operator))
        code.append(ROP(operation, operator))
        code.append(IOP(operation, operator))

    for operation, operator in operations_f.items():
        code.append(OPF(operation, operator))

    for operation in operations_c:
        code.append(OPC(operation, operation))

    return ''.join(code)


class proxy:
    __slots__ = '__factory__', '__wrapped__'

    def __init__(self, factory, *args, **keywords):
        assert callable(factory)
        object.__setattr__(self, '__factory__', (factory, args, keywords))

    def __repr__(self):
        return '<{} object at {} wrapper for {!r}>'.format(
                type(self).__name__, hex(id(self)), self.__wrapped__)

    def __getattribute__(self, name, getattr=getattr,
                            __getattr__=object.__getattribute__):
        if name == '__wrapped__':
            try:
                return __getattr__(self, '__wrapped__')
            except AttributeError:
                factory, args, keywords = __getattr__(self, '__factory__')
                wrapped = factory(*args, **keywords)
                object.__delattr__(self, '__factory__')
                object.__setattr__(self, '__wrapped__', wrapped)
                return wrapped
        else:
            return getattr(self.__wrapped__, name)

    def __setattr__(self, name, value, setattr=setattr):
        setattr(self.__wrapped__, name, value)

    def __delattr__(self, name, delattr=delattr):
        delattr(self.__wrapped__, name)

    def __getitem__(self, key):
        return self.__wrapped__[key]

    def __setitem__(self, key, value):
        self.__wrapped__[key] = value

    def __delitem__(self, key):
        del self.__wrapped__[key]

    def __getslice__(self, i, j):
        return self.__wrapped__[i:j]

    def __setslice__(self, i, j, value):
        self.__wrapped__[i:j] = value

    def __delslice__(self, i, j):
        del self.__wrapped__[i:j]

    def __index__(self):
        wrapped = self.__wrapped__
        try:
            return wrapped.__index__()
        except AttributeError:
            raise TypeError('indices must be integers or slices, not ' + 
                            type(wrapped).__name__)

    def __call__(self, *args, **kwargs):
        return self.__wrapped__(*args, **kwargs)

    exec(create_attr_code())

del create_attr_code


def lazy_import(import_str):
    _import_str = import_str.replace('\\', ' ').lstrip()
    if _import_str.endswith(' *'):
        raise ValueError('lazy_import does not support importing * from a package.')
    elif _import_str.startswith('from '):
        names = _import_str.partition('from ')[2].partition('import ')[2]
    elif _import_str.startswith('import '):
        names = _import_str.partition('import ')[2]
    else:
        raise SyntaxError('invalid import syntax:\n{!r}'.format(import_str))

    def _import(___name):
        if not kv:
            try:
                exec(import_str, f.f_globals, kv)
            except ImportError as e:
                raise RuntimeError(e)
        return kv[___name]

    f = sys._getframe(1)
    is_local_import = f.f_locals is not f.f_globals
    kv = {}
    kvp = {}
    for name in names.strip().strip('()').split(','):
        name = name.rpartition(' as ')[2].strip()
        if is_local_import and name not in f.f_locals:
            raise RuntimeError('LOCAL variables MUST be defined '
                               '(e.g. `{name} = None`) before lazy_import.'
                               .format(**vars()))
        kvp[name] = proxy(_import, name)

    f.f_locals.update(kvp)
    if is_local_import:
        pythonapi.PyFrame_LocalsToFast(py_object(f), c_int(0))
    del kvp
