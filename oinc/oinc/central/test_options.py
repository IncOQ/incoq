"""Unit tests for options.py."""


import unittest
import oinc.incast as L

from .options import *


class DummyManager(OptionsManager):
    normal_defaults = {'a': 'b', 'c': 'd'}
    query_defaults = {'e': 'f', 'g': 'h'}


class OptionsCase(unittest.TestCase):
    
    def test_basic(self):
        query1 = L.pe('COMP({x for x in S}, [S], {"e": "f2"})')
        query2 = L.pe('COMP({y for y in T}, [T], {})')
        
        # Test import/export.
        nopts = {'a': 'b2'}
        qopts = {query1: {'e': 'f2'}}
        o = DummyManager()
        o.import_opts(nopts, qopts)
        
        # Test retrievals.
        self.assertEqual(o.get_opt('a'), 'b2')
        self.assertEqual(o.get_opt('c'), 'd')
        self.assertEqual(o.get_queryopt(query1, 'e'), 'f2')
        self.assertEqual(o.get_queryopt(query1, 'g'), 'h')
        self.assertEqual(o.get_queryopt(query2, 'e'), 'f')
    
    def test_bad_opts(self):
        nopts = {'x': 'y'}
        o = DummyManager()
        with self.assertRaises(L.ProgramError):
            o.validate_nopts(nopts)
        
        query = L.pe('COMP({x for x in S}, [S], {})')
        qopts = {query: {'x': 'y'}}
        o = DummyManager()
        with self.assertRaises(L.ProgramError):
            o.validate_qopts(qopts)


if __name__ == '__main__':
    unittest.main()
