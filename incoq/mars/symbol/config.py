"""Configuration management."""


__all__ = [
    'ConfigAttribute',
    'Config',
    'get_argparser',
    'extract_options',
]


import argparse
from simplestruct import Struct, Field

from .common import parse_bool
from .symbols import Constants


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
    parser = Field()
    """Callable that takes a string to a value for this attribute. If
    None, this attribute is internal and should not be populated by the
    user.
    """
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
        parse_bool,
        {'action': 'store_true'}),
    
    ConfigAttribute('pretend', False,
        'write to standard output instead of the output file',
        parse_bool,
        {'action': 'store_true'}),
    
    ConfigAttribute('obj_domain', False,
        'whether or not the program is in the object-domain',
        parse_bool,
        {'action': 'store_true'}),
    
    ConfigAttribute('default_impl', Constants.Normal,
        'default implementation strategy',
        Constants.parse,
        {'type': Constants.parse}),
    
    ConfigAttribute('unwrap_singletons', False,
        'rewrite singleton relations to eliminate unneeded tuples',
        parse_bool,
        {'action': 'store_true'}),
    
    ConfigAttribute('auto_query', False,
        'if true, automatically wrap comprehensions and aggregates '
        'in QUERY annotations',
        parse_bool,
        {'action': 'store_true'}),
]


class Config:
    
    """A bundle of configuration attributes."""
    
    # Attribute descriptors are pulled in from all_attributes
    # programmatically. (Beware if subclassing Config.)
    
    def __str__(self):
        return '\n'.join('{}: {}'.format(attr.name, getattr(self, attr.name))
                         for attr in all_attributes)
    
    def update(self, *, parse=False, **kargs):
        """Assign to each attribute as specified in keyword arguments."""
        for attr, value in kargs.items():
            descriptor = getattr(type(self), attr, None)
            if not isinstance(descriptor, ConfigAttribute):
                raise ValueError('Unknown config attribute "{}"'.format(attr))
            
            if parse:
                value = descriptor.parser(value)
            
            setattr(self, attr, value)
    
    def parse_and_update(self, **kargs):
        return self.update(parse=True, **kargs)

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
