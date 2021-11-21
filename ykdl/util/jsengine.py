#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
  A simple Javascript engines' wrapper.

  Description:
    This library wraps the Javascript interpreter to python.

    System's built-in Javascript interpreter:

      macOS:   JavascriptCore
      Linux:   Gjs on Gnome, CJS on Cinnamon
      Windows: Chakra

    Any installed external Javascript interpreters, e.g.

      PyChakra, QuickJS, Node.js, etc.

  Usage:

    from jsengine import JSEngine
    
    if JSEngine is None:  # always check this first!
      ...

    ctx = JSEngine()
    ctx.eval('1 + 1')  # => 2

    ctx2 = JSEngine("""
    function add(x, y) {
            return x + y;
        }
        """)
    ctx2.call("add", 1, 2)  # => 3

    ctx.append("""
        function square(x) {
            return x ** 2;
        }
        """)
    ctx.call("square", 9)  # => 81


    If your want use a special external Javascript interpreter, please call
    `ExternalInterpreter` or `set_external_interpreter` after imported:
      
    from jsengine import *

    binary = binary_name or binary_path
    name = None or any_string   # see ExternalInterpreterNameAlias.keys()
    tempfile = True             # use tempfile or not
    evalstring = True           # can run command string as Javascript or can't
    args = [args1, args2, ...]  # arguments used for interpreter

    interpreter = ExternalInterpreter.get(binary, name=name,
                                          tempfile=tempfile,
                                          evalstring=evalstring,
                                          args=args)
    if interpreter:
        # found
        ctx = ExternalJSEngine(interpreter)
      
    if set_external_interpreter(binary, name=name,
                                tempfile=tempfile,
                                evalstring=evalstring,
                                args=args)
        # set default external interpreter OK
        ctx = ExternalJSEngine()
'''

from __future__ import print_function
from subprocess import Popen, PIPE, list2cmdline
import json
import os
import platform
import sys
import tempfile

try:
    from shutil import which
except ImportError:
    from distutils.spawn import find_executable as which


### Before using this library, check JSEngine first!!!
__all__ = ['JSEngine', 'ChakraJSEngine', 'QuickJSEngine', 'ExternalJSEngine',
           'ExternalInterpreter', 'set_external_interpreter',
           'RuntimeError', 'ProgramError']


# Exceptions
_RuntimeError = RuntimeError

class RuntimeError(_RuntimeError):
    pass
    
class ProgramError(Exception):
    pass


# The maximum length of command string
if os.name == 'posix':
    # Used in Unix is ARG_MAX in conf
    ARG_MAX = int(os.popen('getconf ARG_MAX').read())
else:
    # Used in Windows CreateProcess is 32K
    ARG_MAX = 32 * 1024


### Detect Javascript interpreters
chakra_available = False
quickjs_available = False
external_interpreter = None

DefaultExternalInterpreterOptions = {
                # tempfile, evalstring, args
    'ChakraCore': [ True, False, []],
       'Node.js': [ True,  True, []],
       'QuickJS': [ True,  True, []],
            'V8': [ True,  True, []],
            'XS': [ True,  True, []],
}

ExternalInterpreterNameAlias = {
    # *1 Unceremonious name is not recommended to be used as the binary name
        'chakracore': 'ChakraCore',
            'chakra': 'ChakraCore',
                'ch': 'ChakraCore',    # *1
               'cjs': 'CJS',
               'gjs': 'Gjs',
    'javascriptcore': 'JavaScriptCore',
               'jsc': 'JavaScriptCore',
            'nodejs': 'Node.js',
              'node': 'Node.js',
           'quickjs': 'QuickJS',
               'qjs': 'QuickJS',
              'qjsc': 'QuickJS',
      'spidermonkey': 'SpiderMonkey',
                'sm': 'SpiderMonkey',  # *1
                'js': 'SpiderMonkey',  # *1
                'v8': 'V8',            # *1
                'd8': 'V8',            # *1
                'xs': 'XS',            # *1
               'xst': 'XS',
    # Don't use these interpreters
    # They are not compatible with the most used ES6 features
           'duktape': 'Duktape(incompatible)',
               'duk': 'Duktape(incompatible)',
            'hermes': 'Hermes(incompatible)',
           'cscript': 'JScript(incompatible)',
}

# PyChakra
try:
    from PyChakra import Runtime as ChakraHandle, get_lib_path
    if not os.path.exists(get_lib_path()):
        raise RuntimeError
except (ImportError, _RuntimeError):
    pass
else:
    chakra_available = True

# PyQuickJS
try:
    import quickjs
except ImportError:
    pass
else:
    quickjs_available = True

# macOS: built-in JavaScriptCore
if platform.system() == 'Darwin':
    # jsc lives on a new path since macOS Catalina
    jsc_paths = ['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Resources/jsc',
                 '/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc']
    for interpreter in jsc_paths:
        external_interpreter = which(interpreter)
        if external_interpreter:
            break

# Windows: built-in Chakra, or Node.js，QuickJS if installed
elif platform.system() == 'Windows':
    if not chakra_available:
        try:
            from jsengine_chakra import ChakraHandle, chakra_available
        except ImportError:
            from .jsengine_chakra import ChakraHandle, chakra_available

    for interpreter in ('qjs', 'node', 'nodejs'):
        external_interpreter = which(interpreter)
        if external_interpreter:
            break

    if not chakra_available and not quickjs_available and external_interpreter is None:
        print('Please install PyChakra or Node.js!', file=sys.stderr)

# Linux: Gjs on Gnome, CJS on Cinnamon, or JavaScriptCore, Node.js if installed
elif platform.system() == 'Linux':
    for interpreter in ('gjs', 'cjs', 'jsc', 'qjs', 'nodejs', 'node'):
        external_interpreter = which(interpreter)
        if external_interpreter:
            break

    if not chakra_available and not quickjs_available and external_interpreter is None:
        print('''\
Please install at least one of the following Javascript interpreter.'
python packages: PyChakra, quickjs
applications: Gjs, CJS, QuickJS, JavaScriptCore, Node.js, etc.''', file=sys.stderr)

else:
    print('Sorry, the Javascript engine is currently not supported on your system.',
          file=sys.stderr)


# Inject to the script to let it return jsonlized value to python
# Fixed our helper objects
injected_script = u'''\
Object.defineProperty((typeof global !== 'undefined') && global ||
                      (typeof globalThis !== 'undefined') && globalThis ||
                      this, '_JSEngineHelper', {{
    value: {{}},
    writable: false,
    configurable: false
}});
Object.defineProperty(_JSEngineHelper, 'print', {{
    value: typeof print === 'undefined' ? console.log : print,
    writable: false,
    configurable: false
}});
Object.defineProperty(_JSEngineHelper, 'jsonStringify', {{
    value: JSON.stringify,
    writable: false,
    configurable: false
}});
Object.defineProperty(_JSEngineHelper, 'result', {{
    value: null,
    writable: true,
    configurable: false
}});
Object.defineProperty(_JSEngineHelper, 'status', {{
    value: false,
    writable: true,
    configurable: false
}});
try {{
    _JSEngineHelper.result = eval({source}), _JSEngineHelper.status = true;
}}
catch (err) {{
    _JSEngineHelper.result = err.toString(), _JSEngineHelper.status = false;
}}
try {{
    _JSEngineHelper.print('\\n' + _JSEngineHelper.jsonStringify(
        ["result", _JSEngineHelper.status, _JSEngineHelper.result]));
}}
catch (err) {{
    _JSEngineHelper.print(
        '\\n["result", false, "Script returns a value with an unsupported type"]');
}}
'''


# Some simple compatibility processing
init_global_script = u'''\
if (typeof global === 'undefined')
    if (typeof Proxy === 'function')
        global = new Proxy(this, {});
    else
        global = this;
if (typeof globalThis === 'undefined')
    globalThis = this;
'''
init_del_gobject_script = u'''\
if (typeof {gobject} !== 'undefined')
    delete {gobject};
'''

end_split_char = set(u',;\\{}([')

if sys.version_info > (3,):
    unicode = str

def to_unicode(s):
    if not isinstance(s, unicode):
        s = s.decode('utf8')
    return s

def to_bytes(s):
    if isinstance(s, unicode):
        s = s.encode('utf8')
    return s

def json_encoder_fallback(o):
    # Allow bytes (python3)
    if isinstance(o, bytes):
        return to_unicode(o)
    return json.JSONEncoder.default(json_encoder, o)

json_encoder = json.JSONEncoder(
    skipkeys=True,
    ensure_ascii=False,
    check_circular=True,
    allow_nan=True,
    indent=None,
    separators=None,
    default=json_encoder_fallback,
)

json_encoder_ensure_ascii = json.JSONEncoder(
    skipkeys=True,
    ensure_ascii=True,
    check_circular=True,
    allow_nan=True,
    indent=None,
    separators=None,
    default=None,
)


class AbstractJSEngine:
    def __init__(self, source=u'', init_global=False, init_del_gobjects=None):
        self._source = []
        init_script = []
        if init_global:
            init_script.append(init_global_script)
        if init_del_gobjects:
            for gobject in init_del_gobjects:
                init_script.append(init_del_gobject_script.format(gobject=gobject))
        self.append(u''.join(init_script))
        self.append(source)

    @property
    def source(self):
        '''All the inputted Javascript code.'''
        return u'\n'.join(self._source)

    def _append_source(self, code):
        if code:
            self._source.append(code)

    def _check_code(self, code):
        # Input unicode
        code = to_unicode(code)
        last_c = code.rstrip()[-1:]
        if last_c:
            # Simple end-split check
            if last_c not in end_split_char:
                code += u';'
            return code

    def append(self, code):
        '''Run Javascript code and return none.'''
        code = self._check_code(code)
        if code:
            self._append(code)

    def eval(self, code):
        '''Run Javascript code and return result.'''
        code = self._check_code(code)
        if code:
            return self._eval(code)

    def call(self, identifier, *args):
        '''Use name string and arguments to call Javascript function.'''
        chunks = json_encoder.iterencode(args, _one_shot=True)
        chunks = [to_unicode(chunk) for chunk in chunks]
        args = u''.join(chunks)[1:-1]
        code = u'{identifier}({args});'.format(**vars())
        return self._eval(code)

class InternalJSEngine(AbstractJSEngine):
    '''Wrappered for Internal(DLL) Javascript interpreter.'''

    def _append(self, code):
        self._context.eval(code, eval=False, raw=True)

    def _eval(self, code):
        return self._context.eval(code)


class ChakraJSEngine(InternalJSEngine):
    '''Wrappered for system's built-in Chakra or PyChakra(ChakraCore).'''

    def __init__(self, *args, **kwargs):
        if not chakra_available:
            msg = 'No supported Chakra binary found on your system!'
            if quickjs_available:
                msg += ' Please install PyChakra or use QuickJSEngine.'
            elif external_interpreter:
                msg += ' Please install PyChakra or use ExternalJSEngine.'
            else:
                msg += ' Please install PyChakra.'
            raise RuntimeError(msg)
        self._context = self.Context(self)
        InternalJSEngine.__init__(self, *args, **kwargs)

    class Context:
        def __init__(self, engine):
            self._engine = engine
            self._context = ChakraHandle()

        def eval(self, code, eval=True, raw=False):
            self._engine._append_source(code)
            ok, result = self._context.eval(code, raw=raw)
            if ok:
                if eval:
                    return result
            else:
                raise ProgramError(str(result))


class QuickJSEngine(InternalJSEngine):
    '''Wrappered for QuickJS python binding quickjs.'''

    def __init__(self, *args, **kwargs):
        if not quickjs_available:
            msg = 'No supported QuickJS package found on custom python environment!'
            if chakra_available:
                msg += ' Please install python package quickjs or use ChakraJSEngine.'
            elif external_interpreter:
                msg += ' Please install python package quickjs or use ExternalJSEngine.'
            else:
                msg += ' Please install python package quickjs.'
            raise RuntimeError(msg)
        self._context = self.Context(self)
        InternalJSEngine.__init__(self, *args, **kwargs)

    class Context:
        def __init__(self, engine):
            self._engine = engine
            self._context = quickjs.Context()
            self.typeof = self.Function(self, self._context.eval(u'(obj => typeof obj)'))

        def eval(self, code, eval=True, raw=False):
            self._engine._append_source(code)
            try:
                result = self._context.eval(code)
            except quickjs.JSException as e:
                raise ProgramError(*e.args)
            else:
                if eval:
                    if raw or not isinstance(result, quickjs.Object):
                        return result
                    elif callable(result) and self.typeof(result) == u'function':
                        return self.Function(self, result)
                    else:
                        return json.loads(result.json())

        class Function:
            # PetterS/quickjs/Issue7
            # Escape StackOverflow when calling function outside
            def __init__(self, context, function):
                self._context = context
                self._function = function

            def __call__(self, *args):
                return self._function(*args)


class ExternalJSEngine(AbstractJSEngine):
    '''Wrappered for external Javascript interpreter.'''

    def __init__(self, source=u'', init_global=False, init_del_gobjects=[], interpreter=None):
        if isinstance(interpreter, str):
            interpreter = ExternalInterpreter.get(interpreter)
        if isinstance(interpreter, ExternalInterpreter):
            self.interpreter = interpreter
        elif isinstance(external_interpreter, ExternalInterpreter):
            self.interpreter = external_interpreter
        else:
            msg = 'No supported external Javascript interpreter found on your system!'
            if chakra_available:
                msg += ' Please install one or use ChakraJSEngine.'
            elif quickjs_available:
                msg += ' Please install one or use QuickJSEngine.'
            else:
                msg += ' Please install one.'
            raise RuntimeError(msg)
        # Del 'exports' to ignore import error, e.g. Node.js
        init_del_gobjects = list(init_del_gobjects) + ['exports']
        AbstractJSEngine.__init__(self, source, init_global, init_del_gobjects)

    def _append(self, code):
        self._append_source(code)

    def _eval(self, code):
        self._append_source(code)
        code = self._inject_script()

        evalstring = False
        if self.interpreter.evalstring:
            try:
                output = self._run_interpreter_with_string(code)
                evalstring = True
            except ValueError:
                pass
            except _RuntimeError:
                self.interpreter.evalstring = False

        if not evalstring and not self.interpreter.tempfile:
            try:
                output = self._run_interpreter_with_pipe(code)
            except _RuntimeError:
                self.interpreter.tempfile = True

        while True:
            if not evalstring and self.interpreter.tempfile:
                output = self._run_interpreter_with_tempfile(code)

            output = output.replace(u'\r\n', u'\n').replace(u'\r', u'\n')
            # Search result in the last 5 lines of output
            for result_line in output.split(u'\n')[-5:]:
                if result_line[:9] == u'["result"':
                    break
            try:
                _, ok, result = json.loads(result_line)
            except json.decoder.JSONDecodeError as e:
                if not evalstring and self.interpreter.tempfile:
                    raise RuntimeError('%s:\n%s' % (e, output))
                else:
                    evalstring = False
                    self.interpreter.tempfile = True
                    continue
            if ok:
                return result
            else:
                raise ProgramError(result)

    def _run_interpreter(self, cmd, input=None):
        stdin = PIPE if input else None
        p = Popen(cmd, stdin=stdin, stdout=PIPE, stderr=PIPE)
        stdout_data, stderr_data = p.communicate(input=input)
        if p.returncode != 0:
            raise RuntimeError('%r returns non-zero value! Error msg: %s' %
                               (external_interpreter, stderr_data.decode('utf8')))
        elif stderr_data:
            print("%r has warnings:" % external_interpreter, stderr_data.decode('utf8'))
        # Output unicode
        return stdout_data.decode('utf8')

    def _run_interpreter_with_string(self, code):
        # `-e`, `-eval` means run command string as Javascript
        # But some interpreters don't use `-eval`
        cmd = self.interpreter.command + ['-e', code]
        if len(list2cmdline(cmd)) > ARG_MAX:  # Direct compare, don't wait an Exception
            raise ValueError('code length is too long to run as a command')
        return self._run_interpreter(cmd)

    def _run_interpreter_with_pipe(self, code):
        # Input bytes
        return self._run_interpreter(self.interpreter.command, input=to_bytes(code))

    def _run_interpreter_with_tempfile(self, code):
        fd, filename = tempfile.mkstemp(prefix='execjs', suffix='.js')
        try:
            # Write bytes
            with open(fd, 'wb') as fp:
                fp.write(to_bytes(code))
            return self._run_interpreter(self.interpreter.command + [filename])
        finally:
            os.remove(filename)

    def _inject_script(self):
        if self.interpreter.evalstring:
            source = json_encoder_ensure_ascii.encode(self.source)
        else:
            source = json_encoder.encode(self.source)
        return injected_script.format(source=source)


class ExternalInterpreter:
    '''Create an external interpreter setting.'''

    @classmethod
    def get(cls, *args, **kwargs):
        try:
            return cls(*args, **kwargs)
        except Exception as e:
            print(e, file=sys.stderr)

    def __init__(self, interpreter, name=None, tempfile=False, evalstring=False, args=None):
        path = which(interpreter)
        if path is None:
            raise ValueError('Can not find the given interpreter: %r' % interpreter)
        filename = os.path.basename(path).split('.')[0]
        if name is None:
            name = filename
        name = ExternalInterpreterNameAlias.get(name.lower().replace('.', ''), name)
        if name in DefaultExternalInterpreterOptions:
            tempfile, evalstring, args = DefaultExternalInterpreterOptions[name]
        self.name = name
        self.path = path
        self.tempfile = tempfile
        self.evalstring = evalstring
        self.command = [path]
        if args:
            self.command += list(args)

    def __repr__(self):
        return '<ExternalInterpreter %s @ %r>' % (self.name, self.path)


def set_external_interpreter(interpreter, *args, **kwargs):
    '''
    Set default an external interpreter, return the resoult status.
    Same arguments as the ExternalInterpreter.
    '''
    global external_interpreter
    interpreter = ExternalInterpreter.get(interpreter, *args, **kwargs)
    if interpreter:
        external_interpreter = interpreter
    return interpreter


if external_interpreter:
    external_interpreter = ExternalInterpreter(external_interpreter)

# Prefer InternalJSEngine (via dynamic library loading)
if chakra_available:
    JSEngine = ChakraJSEngine
elif quickjs_available:
    JSEngine = QuickJSEngine
elif external_interpreter:
    JSEngine = ExternalJSEngine
else:
    JSEngine = None


if __name__ == '__main__':
    # Run test
    import subprocess
    cmds = [sys.executable, 'jsengine_test.py']
    subprocess.Popen(cmds)
