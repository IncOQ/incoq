"""Unit tests for config.py."""


import unittest

from incoq.mars.config import *
from incoq.mars.config import all_attributes


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


if __name__ == '__main__':
    unittest.main()
