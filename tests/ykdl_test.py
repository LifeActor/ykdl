#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ykdl.compact import compact_unquote, compact_bytes

class TestCompat(unittest.TestCase):

    def test_compat_unquote(self):
        self.assertEqual(compact_unquote('abc%20def'), 'abc def')
        self.assertEqual(compact_unquote('%7e/abc+def'), '~/abc+def')
        self.assertEqual(compact_unquote(''), '')
        self.assertEqual(compact_unquote('%'), '%')
        self.assertEqual(compact_unquote('%%'), '%%')
        self.assertEqual(compact_unquote('%%%'), '%%%')
        self.assertEqual(compact_unquote('%2F'), '/')
        self.assertEqual(compact_unquote('%2f'), '/')
        self.assertEqual(compact_unquote('%E6%B4%A5%E6%B3%A2'), u'津波')
        self.assertEqual(
            compact_unquote('''<meta property="og:description" content="%E2%96%81%E2%96%82%E2%96%83%E2%96%84%25%E2%96%85%E2%96%86%E2%96%87%E2%96%88" />
%<a href="https://ar.wikipedia.org/wiki/%D8%AA%D8%B3%D9%88%D9%86%D8%A7%D9%85%D9%8A">%a'''),
            u'''<meta property="og:description" content="▁▂▃▄%▅▆▇█" />
%<a href="https://ar.wikipedia.org/wiki/تسونامي">%a''')
        self.assertEqual(
            compact_unquote('''%28%5E%E2%97%A3_%E2%97%A2%5E%29%E3%81%A3%EF%B8%BB%E3%83%87%E2%95%90%E4%B8%80    %E2%87%80    %E2%87%80    %E2%87%80    %E2%87%80    %E2%87%80    %E2%86%B6%I%Break%25Things%'''),
u'''(^◣_◢^)っ︻デ═一    ⇀    ⇀    ⇀    ⇀    ⇀    ↶%I%Break%Things%''')

    def test_compact_bytes(self):
        self.assertEqual(compact_bytes('abc', 'utf-8'), 'abc'.encode('utf-8'))
        self.assertEqual(compact_bytes(u'你好', 'utf-8'), u'你好'.encode('utf-8'))

if __name__ == '__main__':
    unittest.main()
