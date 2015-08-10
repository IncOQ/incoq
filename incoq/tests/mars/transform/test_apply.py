"""Unit tests for apply.py."""


import unittest

from incoq.mars.incast import P
from incoq.mars.transform.apply import *


class ApplyCase(unittest.TestCase):
    
    def test_transform_source(self):
        source = P.trim('''
            import incoq.mars.runtime as runtime
            def main():
                a = b = c
            ''')
        source = transform_source(source)
        exp_source = P.trim('''
            from incoq.mars.runtime import *
            def main():
                b = c
                a = b
            
            ''')
        self.assertEqual(source, exp_source)


if __name__ == '__main__':
    unittest.main()
