"""Unit tests for config.py."""


import unittest
import argparse

from incoq.mars.symbol.config import *
from incoq.mars.symbol.config import all_attributes


class ConfigCase(unittest.TestCase):
    
    def test_attr_descriptor(self):
        # Grab "verbose" as the representative example attribute to use.
        for attr in all_attributes:
            if attr.name == 'verbose':
                verb = attr
                break
        else:
            assert()
        
        # Check default value, setting, and getting.
        config = Config()
        self.assertEqual(config.verbose, verb.default)
        config.verbose = not config.verbose
        self.assertNotEqual(config.verbose, verb.default)
        
        # Check that class-level attribute retrieval returns the
        # descriptor.
        self.assertIs(Config.verbose, verb)
    
    def test_update(self):
        config = Config()
        
        # Normal case.
        config.update(verbose=True)
        self.assertEqual(config.verbose, True)
        
        # Bad attr name.
        with self.assertRaises(ValueError):
            config.update(_bad=True)
    
    def test_parse_and_update(self):
        config = Config()
        config.parse_and_update(verbose='True')
        self.assertEqual(config.verbose, True)
    
    def test_argparser(self):
        parent = get_argparser()
        child = argparse.ArgumentParser(parents=[parent])
        child.add_argument('foo')
        
        ns = child.parse_args(['abc', '--verbose'])
        self.assertEqual(ns.verbose, True)
        self.assertEqual(ns.pretend, False)
        self.assertEqual(ns.foo, 'abc')
        
        options = extract_options(ns)
        self.assertEqual(options.get('verbose', None), True)
        self.assertEqual(options.get('pretend', None), False)
        self.assertNotIn('foo', options)


if __name__ == '__main__':
    unittest.main()
