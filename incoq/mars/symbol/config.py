"""Configuration management."""


__all__ = [
    'ConfigAttribute',
    'Config',
    'get_argparser',
    'extract_options',
]


import argparse
from simplestruct import Struct, Field

from incoq.mars.type import T

from .common import parse_bool
from .symbols import Constants


def parse_typedef(s, symtab=None):
    typedefs = {}
    lines = [line for line in s.split(';')
                  if line and not line.isspace()]
    for line in lines:
        name, definition = line.split('=')
        name = name.strip()
        t = T.eval_typestr(definition, typedefs)
        typedefs[name] = t
    return typedefs


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
    
    ConfigAttribute('default_demand_set_maxsize', None,
        'default value for demand_set_maxsize',
        int,    # Should really use a better parse function
                # that also supports None
        {'type': int}),
    
    ConfigAttribute('use_singletag_demand', False,
        'if True, only use one tag in the definition of each filter',
        parse_bool,
        {'action': 'store_true'}),
    
    ConfigAttribute('unwrap_singletons', False,
        'rewrite singleton relations to eliminate unneeded tuples',
        parse_bool,
        {'action': 'store_true'}),
    
    # TODO: Need to refactor this to separate config options from
    # parser options, so we can have --no-auto-query, --no-inline...,
    # etc., that have 'store_false' as an action.
    
    ConfigAttribute('auto_query', False,
        'if true, automatically wrap comprehensions and aggregates '
        'in QUERY annotations',
        parse_bool,
        {'action': 'store_true'}),
    
    ConfigAttribute('inline_maint_code', False,
        'if true, inline inserted maintenance functions',
        parse_bool,
        {'action': 'store_true'}),
    
    ConfigAttribute('elim_counts', True,
        'if true, eliminate counts where we can infer it\'s safe to '
        'do so',
        parse_bool,
        {'action': 'store_true'}),
    
    ConfigAttribute('elim_dead_relations', True,
        'if true, eliminate dead relations',
        parse_bool,
        {'action': 'store_true'}),
    
    ConfigAttribute('elim_type_checks', True,
        'if true, eliminate type checks where safe',
        parse_bool,
        {'action': 'store_true'}),
    
    ConfigAttribute('elim_dead_funcs', True,
        'if true, eliminate uncalled maintenance functions',
        parse_bool,
        {'action': 'store_true'}),
    
    ConfigAttribute('distalgo_mode', True,
        'enable special rewritings for DistAlgo inc interface',
        parse_bool,
        {'action': 'store_true'}),
    
    ConfigAttribute('typedefs', {},
        'mapping from type identifiers to type definition',
        parse_typedef,
        {}),
    
    ConfigAttribute('costs', True,
        'write cost annotation comments',
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
