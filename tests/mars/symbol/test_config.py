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
                assert verb.default is False
                break
        else:
            assert()
        
        # Check default value, setting, and getting.
        config = Config()
        self.assertEqual(config.verbose, False)
        config.verbose = not config.verbose
        self.assertEqual(config.verbose, True)
        
        # Check that class-level attribute retrieval returns the
        # descriptor.
        self.assertIs(Config.verbose, verb)
    
    def test_parse_and_update(self):
        config = Config()
        assert config.verbose is False
        config.parse_and_update(verbose='True')
        self.assertEqual(config.verbose, True)
        
        # Ignore missing key or None-mapped key.
        config.parse_and_update(verbose=None)
        self.assertEqual(config.verbose, True)
        config.parse_and_update()
        self.assertEqual(config.verbose, True)
        
        # Bad attr name.
        with self.assertRaises(ValueError):
            config.parse_and_update(_bad=True)
    
    def test_argparser(self):
        parent = get_argparser()
        child = argparse.ArgumentParser(parents=[parent])
        child.add_argument('foo', nargs='?')
        
        # With the option supplied.
        ns = child.parse_args(['abc', '--verbose'])
        self.assertEqual(ns.verbose, 'true')
        self.assertEqual(ns.foo, 'abc')
        options = extract_options(ns)
        exp_options = {'verbose': 'true'}
        self.assertEqual(options, exp_options)
        
        # With the option omitted.
        ns = child.parse_args([])
        self.assertEqual(ns.verbose, None)
        options = extract_options(ns)
        exp_options = {}
        self.assertEqual(options, exp_options)
        
        # With the --no- prefixed option supplied.
        ns = child.parse_args(['--no-verbose'])
        self.assertEqual(ns.verbose, 'false')
        
        # With an enum option.
        ns = child.parse_args(['--default-impl', 'normal'])
        self.assertEqual(ns.default_impl, 'normal')
        
        # With an int/none option.
        ns = child.parse_args(['--default-demand-set-maxsize', 'none'])
        self.assertEqual(ns.default_demand_set_maxsize, 'none')
        ns = child.parse_args(['--default-demand-set-maxsize', '5'])
        self.assertEqual(ns.default_demand_set_maxsize, '5')


if __name__ == '__main__':
    unittest.main()
