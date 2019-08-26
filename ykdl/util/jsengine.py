#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Simple Javascript engines' wrapper

    Description:
        This library wraps the system's built-in Javascript interpreter to python.
        It also support PyChakra.

    Platform:
        macOS:   Use JavascriptCore
        Linux:   Use gjs on Gnome, cjs on Cinnamon or NodeJS if installed
        Windows: Use Win10's built-in Chakra, if not available use NodeJS

        PyChakra can run in all the above.

    Usage:

        from jsengine import JSEngine
        
        if JSEngine is None:  # always check this first!
            ......

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
'''

from __future__ import print_function
from subprocess import Popen, PIPE
import io
import json
import os
import platform
import sys
import tempfile

try:
    from shutil import which
except ImportError:
    from distutils.spawn import find_executable as which


__all__ = ['ProgramError', 'ChakraJSEngine', 'ExternalJSEngine', 'JSEngine']


### Before using this library, check this variable first!!!
# **DEPRECATED**
# Now, we check JSEngine directly.
javascript_is_supported = True

# Exceptions
class ProgramError(Exception):
    pass


### Detect javascript interpreters
chakra_available = False
interpreter = None

# PyChakra
try:
    from PyChakra import Runtime as ChakraHandle, get_lib_path
    get_lib_path()
except (ImportError, RuntimeError):
    pass
else:
    chakra_available = True

# macOS: built-in JavaScriptCore
if platform.system() == 'Darwin':
    interpreter = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Resources/jsc'

# Windows: built-in Chakra, Node.js if installed
elif platform.system() == 'Windows':
    if not chakra_available:
        try:
            from jsengine_chakra import ChakraHandle, chakra_available
        except ImportError:
            from .jsengine_chakra import ChakraHandle, chakra_available

    interpreter = which('node')

    if not chakra_available and interpreter is None:
        print('Please install PyChakra or Node.js!', file=sys.stderr)
        javascript_is_supported = False

# Linux: gjs on Gnome, cjs on Cinnamon or JavaScriptCore/NodeJS if installed
elif platform.system() == 'Linux':
    for interpreter in ('gjs', 'cjs', 'jsc', 'nodejs', 'node'):
        interpreter = which(interpreter)
        if interpreter:
            break

    if not chakra_available and interpreter is None:
        print('Please install at least one of the following Javascript interpreter'
              ': PyChakra, gjs, cjs, jsc, nodejs', file=sys.stderr)
        javascript_is_supported = False

else:
    print('Sorry, the Javascript engine is currently not supported on your system',
          file=sys.stderr)
    javascript_is_supported = False


# Inject to the script to let it return jsonlized value to python
# The additional code run only once, it does not require isolation processing
injected_script = u'''\
{source}
try {{
    var result = eval({data}), status = true;
}}
catch (err) {{
    var result = '' + err, status = false;
}}
try {{
    print('\\n' + JSON.stringify([status, result]));
}}
catch (err) {{
    print('\\n[false, "Script returns a value with an unsupported type"]');
}}
'''


# Some simple compatibility processing
init_print_script = u'''\
if (typeof print === 'undefined' && typeof console === 'object') {
    print = console.log;
}
'''
init_global_script = u'''\
if (typeof global === 'undefined') {
    global = new Proxy(this, {});
}
'''
init_del_gvar_script = u'''\
if (typeof {gvar} === 'object') {{
    {gvar} = undefined;
}}
'''
init_del_gvars = ['exports']

end_split_char = set(u';)}')

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
    return json_encoder.default(o)

json_encoder = json.JSONEncoder(
    skipkeys=True,
    ensure_ascii=False,
    check_circular=True,
    allow_nan=True,
    indent=None,
    separators=None,
    default=json_encoder_fallback,
)


class AbstractJSEngine:
    def __init__(self, source=u'', init_global=True, init_del_gvars=init_del_gvars):
        self._source = []
        init_script = [init_print_script]
        if init_global:
            init_script.append(init_global_script)
        if init_del_gvars:
            for gvar in init_del_gvars:
                if gvar == 'print' and hasattr(self, '_tempfile'):
                    continue
                init_script.append(init_del_gvar_script.format(gvar=gvar))
        init_script = u''.join(init_script)
        self.append(init_script)
        self.append(source)

    @property
    def source(self):
        return self._get_source()

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
        code = self._check_code(code)
        if code:
            self._append(code)

    def eval(self, code):
        code = self._check_code(code)
        if code:
            return self._eval(code)

    def call(self, identifier, *args):
        chunks = json_encoder.iterencode(args, _one_shot=True)
        chunks = [to_unicode(chunk) for chunk in chunks]
        args = u''.join(chunks)[1:-1]
        code = u'{identifier}({args})'.format(identifier=identifier, args=args)
        return self._eval(code)


class ChakraJSEngine(AbstractJSEngine):
    def __init__(self, source=u''):
        if not chakra_available:
            msg = 'No supported chakra binary found on your system!'
            if interpreter:
                msg += 'Please install PyChakra or use ExternalJSEngine.'
            raise RuntimeError(msg)
        self.chakra = ChakraHandle()
        AbstractJSEngine.__init__(self, source)

    def _get_source(self):
        return u'\n'.join(self._source)

    def _append(self, code):
        self._append_source(code)
        ok, result = self.chakra.eval(code, True)
        if not ok:
            raise ProgramError(str(result))

    def _eval(self, code):
        self._append_source(code)
        ok, result = self.chakra.eval(code)
        if ok:
            return result
        else:
            raise ProgramError(str(result))


class ExternalJSEngine(AbstractJSEngine):
    def __init__(self, source=u''):
        if not interpreter:
            if chakra_available:
                msg = ('ExternalJSEngine is not available now! Please install '
                       'a Javascript interpreter or use ChakraJSEngine.')
            else:
                msg = 'No supported Javascript interpreter found on your system!'
            raise RuntimeError(msg)
        self._last_code = u''
        self._tempfile = False
        AbstractJSEngine.__init__(self, source)

    def _get_source(self, last_code=True):
        if last_code and self._last_code:
            source = self._source + [self._last_code]
        else:
            source = self._source
        return u'\n'.join(source)

    def _append(self, code):
        self._append_source(self._last_code)
        self._last_code = code

    def _eval(self, code):
        self._append(code)
        code = self._inject_script(code)
        if not self._tempfile:
            try:
                output = self._run_interpreter_with_pipe(code)
            except RuntimeError:
                self._tempfile = True
        if self._tempfile:
            output = self._run_interpreter_with_tempfile(code)

        output = output.replace(u'\r\n', u'\n').replace(u'\r', u'\n')
        for result_line in output.split(u'\n')[-3:]:
            if result_line[:1] == u'[':
                break
        ok, result = json.loads(result_line)
        if ok:
            return result
        else:
            raise ProgramError(result)

    def _run_interpreter(self, cmd, stdin=None, input=None):
        p = None
        try:
            p = Popen(cmd, stdin=stdin, stdout=PIPE, stderr=PIPE)
            stdoutdata, stderrdata = p.communicate(input=input)
            ret = p.wait()
        finally:
            del p
        if ret != 0:
            raise RuntimeError('Javascript interpreter returns non-zero value! '
                               'Error msg: %s' % stderrdata.decode('utf8'))
        # Output unicode
        return stdoutdata.decode('utf8')

    def _run_interpreter_with_pipe(self, code):
        cmd = [interpreter]
        # Input bytes
        code = to_bytes(code)
        return self._run_interpreter(cmd, stdin=PIPE, input=code)

    def _run_interpreter_with_tempfile(self, code):
        (fd, filename) = tempfile.mkstemp(prefix='execjs', suffix='.js')
        os.close(fd)
        try:
            # Write bytes
            code = to_bytes(code)
            with io.open(filename, 'wb') as fp:
                fp.write(code)

            cmd = [interpreter, filename]
            return self._run_interpreter(cmd)
        finally:
            os.remove(filename)

    def _inject_script(self, code):
        source = self._get_source(last_code=False)
        data = json_encoder.encode(code)
        return injected_script.format(source=source, data=data)


# Prefer ChakraJSEngine (via dynamic library loading)
if chakra_available:
    JSEngine = ChakraJSEngine
elif javascript_is_supported:
    JSEngine = ExternalJSEngine
else:
    JSEngine = None


if __name__ == '__main__':
    #interpreter = 'S:/jsshell-win64/js'
    #interpreter = 'S:/node/node'
    for JSEngine in (ChakraJSEngine, ExternalJSEngine):
        try:
            print('start test %s:' % JSEngine.__name__)
            ctx = JSEngine()
            assert ctx._eval('') is None, 'eval empty fail!'
            assert ctx.eval('1 + 1') == 2, 'eval fail!'
            assert ctx.eval('[1, 2]') == [1, 2], 'eval fail!'
            assert ctx.eval('[void((()=>{})()), 1]') == [None, 1], 'eval fail!'
            assert ctx.eval('(()=>{return {a: 2}})()')['a'] == 2, 'eval fail!'
            print(ctx.eval('"es:αβγ"'))
            print(ctx.eval(u'"eu:αβγ"'))
            print(ctx.eval(to_bytes('"eb:αβγ"')))
            if JSEngine is ExternalJSEngine:
                ctx.append('ping=((s1,s2,s3)=>{return [s1,s2,s3]})')
                # Mixed string types input
                print(ctx.call('ping', 'cs:αβγ', u'cu:αβγ', to_bytes('cb:αβγ')))
            print('source code:')
            print(ctx.source)
            try:
                ctx.eval('a')
            except Exception as e:
                assert 'ReferenceError' in e.args[0], 'exception fail!'
        except:
            import traceback
            traceback.print_exception(*sys.exc_info())
        finally:
            print('end test %s' % JSEngine.__name__)
    if platform.system() == 'Windows':
        import msvcrt
        msvcrt.getch()
