#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Simple Javascript engines' wrapper

    Description:
        This library wraps the system's built-in Javascript interpreter to python.

    Platform:
        macOS:   Use JavascriptCore
        Linux:   Use gjs on Gnome, cjs on Cinnamon or NodeJS if installed
        Windows: Use Win10's built-in Chakra, if not available use NodeJS

    Usage:

        from jsengine import JSEngine, javascript_is_supported
        
        if not javascript_is_supported:  # always check this first!
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
from distutils.spawn import find_executable
from subprocess import Popen, PIPE
import io
import json
import os
import platform
import re
import sys
import tempfile

__all__ = ['ProgramError', 'javascript_is_supported', 'interpreter',
           'ChakraJSEngine', 'ExternalJSEngine', 'JSEngine']

### Before using this library, check this variable first!!!
javascript_is_supported = True

# Exceptions
class ProgramError(Exception):
    pass


use_chakra = False
interpreter = []

# Choose javascript interpreter
# Try PyChakra
try:
    from PyChakra import Runtime as ChakraHandle, get_lib_path
    get_lib_path()
except (ImportError, RuntimeError):
    pass
else:
    use_chakra = True
if use_chakra:
    pass

# macOS: use built-in JavaScriptCore
elif platform.system() == 'Darwin':
    interpreter = ['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Resources/jsc']

# Windows: Try Chakra, if fails, load Node.js
elif platform.system() == 'Windows':
    try:
        from jsengine_chakra import ChakraHandle, chakra_available
    except ImportError:
        from .jsengine_chakra import ChakraHandle, chakra_available
    if chakra_available:
        use_chakra = True
    elif find_executable('node') is not None:
        interpreter = ['node']
    else:
        print('Please install PyChakra or Node.js!', file=sys.stderr)
        javascript_is_supported = False

# Linux: use gjs on Gnome, cjs on Cinnamon or JavaScriptCore/NodeJS if installed
elif platform.system() == 'Linux':
    if find_executable('gjs') is not None:
        interpreter = ['gjs']
    elif find_executable('cjs') is not None:
        interpreter = ['cjs']
    elif find_executable('jsc') is not None:
        interpreter = ['jsc']
    elif find_executable('nodejs') is not None:
        interpreter = ['nodejs']
    elif find_executable('node') is not None:
        interpreter = ['node']
    else:
        print('Please install at least one of the following Javascript interpreter'
              ': PyChakra, gjs, cjs, nodejs', file=sys.stderr)
        javascript_is_supported = False

else:
    print('Sorry, the Javascript engine is currently not supported on your system',
          file=sys.stderr)
    javascript_is_supported = False



# Inject to the script to let it return jsonlized value to python
injected_script = '''\
var exports = undefined;
(function(program, execJS) { execJS(program) })(
function() {
    #{encoded_source}
},
function(program) {
    var print = (this.print === undefined) ? console.log : this.print;
    try {
        result = program();
        print("");
        if (typeof result == 'undefined' && result !== null) {
            print('["ok"]');
        }
        else {
            try {
                print(JSON.stringify(['ok', result]));
            }
            catch (err) {
                print('["err", "Script returns a value with an unknown type"]');
            }
        }
    }
    catch (err) {
        print(JSON.stringify(['err', '' + err]));
    }
});
'''



class AbstractJSEngine:
    def __init__(self, source=''):
        self._source = []
        self.append(source)

    @property
    def source(self):
        return self._get_source()

    def _append_source(self, code):
        self._source.append(code)
        # Simple end-split check
        if code.lstrip()[-1:] not in ';,)}':
            self._source.append(';')

    def append(self, code):
        if code.strip():
            self._append(code)

    def call(self, identifier, *args):
        args = json.dumps(args)
        code = '{identifier}.apply(this,{args})'.format(identifier=identifier, args=args)
        return self._eval(code)

    def eval(self, code=''):
        if code.strip():
            return self._eval(code)


class ChakraJSEngine(AbstractJSEngine):
    def __init__(self, source=''):
        if not chakra_available:
            raise RuntimeError('No supported chakra binary found on your system!')
        self.chakra = ChakraHandle()
        AbstractJSEngine.__init__(self, source)

    def _get_source(self):
        return '\n'.join(self._source)

    def _append(self, code):
        self._append_source(code)
        ok, result = self.chakra.eval(code)
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
    def __init__(self, source=''):
        if not interpreter:
            raise RuntimeError('No supported Javascript interpreter found on your system!')
        self._last_code = ''
        AbstractJSEngine.__init__(self, source)

    def _get_source(self, last_code=None):
        if last_code is None:
            last_code = self._last_code
        if last_code:
            source = self._source + [last_code]
        else:
            source = self._source
        return '\n'.join(source)

    def _append(self, code):
        if self._last_code:
            self._append_source(self._last_code)
        self._last_code = code

    def _eval(self, code):
        self._append(code)
        code = self._inject_script(code)
        output = self._run_interpreter_with_tempfile(code)
        output = output.replace('\r\n', '\n').replace('\r', '\n')
        last_line = output.split('\n')[-2]
        ret = json.loads(last_line)
        if len(ret) == 1:
            return None
        status, value = ret
        if status == 'ok':
            return value
        else:
            raise ProgramError(value)

    def _run_interpreter_with_tempfile(self, code):
        (fd, filename) = tempfile.mkstemp(prefix='execjs', suffix='.js')
        os.close(fd)
        try:
            # Decoding in python2
            if hasattr(code, 'decode'):
                code = code.decode('utf8')
            with io.open(filename, 'w', encoding='utf8') as fp:
                fp.write(code)

            cmd = interpreter + [filename]
            p = None
            try:
                p = Popen(cmd, stdout=PIPE, universal_newlines=True)
                # Wrapped output with 'utf8' encoding
                p.stdout = FileWrapper(p.stdout, encoding='utf8')
                stdoutdata, stderrdata = p.communicate()
                ret = p.wait()
            finally:
                del p
            if ret != 0:
                raise RuntimeError('Javascript interpreter returns non-zero value!')
            return stdoutdata
        finally:
            os.remove(filename)

    def _inject_script(self, code):
        source = self._get_source('')
        source = encode_unicode_codepoints(source)
        data = json.dumps(code)
        encoded_source = '''\
        {source}
        return eval({data});'''.format(source=source, data=data)
        return injected_script.replace('#{encoded_source}', encoded_source)


if use_chakra:
    JSEngine = ChakraJSEngine
else:
    JSEngine = ExternalJSEngine


# Used for code input to support non-ascii encoding
def encode_unicode_codepoints(str):
    codepoint_format = '\\u{0:04x}'.format
    def codepoint(m):
        return codepoint_format(ord(m.group(0)))
    return re.sub('[^\x00-\x7f]', codepoint, str)


# Used for PIPE ouput to support non-ascii encoding
if sys.version_info[0] < 3:
    class FileWrapper(object):
        def __init__(self, file, encoding, errors='strict'):
            object.__setattr__(self, 'wrappedfile', file)
            object.__setattr__(self, 'encoding', encoding)
            object.__setattr__(self, 'errors', errors)

        def __getattr__(self, name):
            return getattr(self.wrappedfile, name)

        def __setattr__(self, name, value):
            setattr(self.wrappedfile, name, value)

        def write(self, s):
            if isinstance(s, unicode):
                s = s.encode(encoding=self.encoding, errors=self.errors)
            self.wrappedfile.write(s)
else:
    def FileWrapper(file, encoding, errors='strict'):
        return io.TextIOWrapper(file.detach(),
                                encoding=encoding,
                                errors=errors,
                                line_buffering=True)


if __name__ == '__main__':
    #interpreter = ['S:/jsshell-win64/js']
    #interpreter = ['S:/node/node']
    for JSEngine in (ChakraJSEngine, ExternalJSEngine):
        try:
            ctx = JSEngine()
            assert ctx._eval('') is None, 'eval empty fail!'
            assert ctx.eval('1 + 1') == 2, 'eval fail!'
            assert ctx.eval('[1, 2]') == [1, 2], 'eval fail!'
            assert ctx.eval('[void((()=>{})()), 1]') == [None, 1], 'eval fail!'
            assert ctx.eval('(() => {return {a: 2}})()')['a'] == 2, 'eval fail!'
            print(ctx.eval(u'"αβγ"'))
            try:
                ctx.eval('a')
            except Exception as e:
                assert 'ReferenceError' in e.args[0], 'exception fail!'
        except:
            import traceback
            traceback.print_exception(*sys.exc_info())
    if platform.system() == 'Windows':
        import msvcrt
        msvcrt.getch()
