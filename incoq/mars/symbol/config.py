"""Configuration management."""


__all__ = [
    'ConfigAttribute',
    'Config',
    'get_argparser',
    'extract_options',
]


import argparse
from simplestruct import Struct, Field

from .symbols import Constants


def parse_constant(v):
    d = {k.lower(): v for k, v in Constants.__members__.items()}
    return d[v]


# Each configuration attribute is a descriptor, listed in the
# all_attributes list, and put in the class namespace for Config.
# The order of all_attributes is canonical for user documentation
# purposes.


class ConfigAttribute(Struct):
    
    """Descriptor for a configuration attribute."""
    
    # The actual attribute value, if it exists, is stored on the
    # instance under the name of the attribute prefixed with an
    # underscore.
    
    name = Field()
    """Name of attribute."""
    default = Field()
    """Default value."""
    docstring = Field()
    """User documentation."""
    argparse_kargs = Field()
    """Dictionary to pass along as **kargs to argparse's add_argument()
    function.
    """
    
    def __get__(self, inst, owner):
        if inst is None:
            return self
        
        # Return default if it doesn't exist.
        return getattr(inst, '_' + self.name, self.default)
    
    def __set__(self, inst, value):
        setattr(inst, '_' + self.name, value)


all_attributes = [
    ConfigAttribute('verbose', False,
        'print transformation information to standard output',
        {'action': 'store_true'}),
    
    ConfigAttribute('pretend', False,
        'write to standard output instead of the output file',
        {'action': 'store_true'}),
    
    ConfigAttribute('obj_domain', False,
        'whether or not the program is in the object-domain',
        {'action': 'store_true'}),
    
    ConfigAttribute('default_impl', Constants.Normal,
        'default implementation strategy',
        {'type': parse_constant}),
    
    ConfigAttribute('unwrap_singletons', False,
        'rewrite singleton relations to eliminate unneeded tuples',
        {'action': 'store_true'}),
]


class Config:
    
    """A bundle of configuration attributes."""
    
    # Attribute descriptors are pulled in from all_attributes
    # programmatically. (Beware if subclassing Config.)
    
    def __str__(self):
        return '\n'.join('{}: {}'.format(attr.name, getattr(self, attr.name))
                         for attr in all_attributes)
    
    def update(self, **kargs):
        """Assign to each attribute as specified in keyword arguments."""
        for attr, value in kargs.items():
            descriptor = getattr(type(self), attr, None)
            if not isinstance(descriptor, ConfigAttribute):
                raise ValueError('Unknown config attribute "{}"'.format(attr))
            setattr(self, attr, value)

for attr in all_attributes:
    setattr(Config, attr.name, attr)


def get_argparser():
    """Return a parent parser for the configuration options."""
    parser = argparse.ArgumentParser(add_help=False)
    for attr in all_attributes:
        parser.add_argument('--' + attr.name,
                            help=attr.docstring,
                            default=attr.default,
                            **attr.argparse_kargs)
    return parser


def extract_options(namespace):
    """Given an argument parser namespace, return an options dictionary
    for all configuration options.
    """
    return {attr.name: getattr(namespace, attr.name)
            for attr in all_attributes}
