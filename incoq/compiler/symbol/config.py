"""Configuration management."""


__all__ = [
    'Config',
    'get_argparser',
    'extract_options',
]


import argparse

from incoq.compiler.type import T

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


class BaseConfigAttribute:
    
    """Descriptor for a configuration attribute."""
    
    def __init__(self, name, default_str, docstring):
        self.name = name
        """Name of config attribute."""
        self.default_str = default_str
        """String representation of default value."""
        self.docstring = docstring
        """User documentation / description of config attribute."""
        
        self.default = self.parse(default_str)
    
    def parse(self, s):
        """Given a string, return a parsed value for this attribute,
        or raise ValueError if the string is unacceptable.
        """
        return s
    
    def update_argparser(self, argparser, *, with_help=True):
        """Given an argparse.ArgumentParser object, update it to be
        able to parse the command line options corresponding to this
        config attribute. If with_help is False, do not generate help
        messages for the added options.
        """
        pass
    
    # The underlying value is stored in a '_'-prefixed version of the
    # config attribute's name.
    
    def __get__(self, inst, owner):
        if inst is None:
            return self
        
        # Return default if it doesn't exist.
        return getattr(inst, '_' + self.name, self.default)
    
    def __set__(self, inst, value):
        setattr(inst, '_' + self.name, value)


class BooleanConfigAttribute(BaseConfigAttribute):
    
    """Configuration attribute that can take on true/false values."""
    
    def __init__(self, name, default_str, docstring):
        super().__init__(name, default_str, docstring)
        assert isinstance(self.default, bool)
    
    def parse(self, s):
        return parse_bool(s)
    
    def update_argparser(self, argparser, *, with_help=True):
        argname = self.name.replace('_', '-')
        
        if with_help:
            # Choose whether help for the normal or negated version
            # is visible.
            if self.default is False:
                positive_help = self.docstring
                negative_help = argparse.SUPPRESS
            else:
                positive_help = argparse.SUPPRESS
                negative_help = '(disable) ' + self.docstring
        else:
            positive_help = argparse.SUPPRESS
            negative_help = argparse.SUPPRESS
        
        argparser.add_argument('--' + argname,
                               help=positive_help,
                               action='store_const',
                               const='true',
                               dest=self.name)
        argparser.add_argument('--no-' + argname,
                               help=negative_help,
                               action='store_const',
                               const='false',
                               dest=self.name)


class EnumConfigAttribute(BaseConfigAttribute):
    
    """Configuration attribute that can take on some Constant values."""
    
    def __init__(self, name, default_str, docstring, allowed):
        super().__init__(name, default_str, docstring)
        assert isinstance(self.default, Constants)
        self.allowed = allowed
        assert all(isinstance(self.parse(v), Constants)
                   for v in allowed)
    
    def parse(self, s):
        return Constants.parse(s)
    
    def update_argparser(self, argparser, *, with_help=True):
        argname = self.name.replace('_', '-')
        
        if with_help:
            docstring = '{} (default: {})'.format(
                self.docstring, self.default_str)
        else:
            docstring = argparse.SUPPRESS
        
        argparser.add_argument('--' + argname,
                               help=docstring,
                               action='store',
                               choices=self.allowed,
                               dest=self.name)


class IntNoneConfigAttribute(BaseConfigAttribute):
    
    """Configuration attribute that can take on some Constant values."""
    
    def __init__(self, name, default_str, docstring):
        super().__init__(name, default_str, docstring)
    
    def parse(self, s):
        if s.lower().strip() == 'none':
            return None
        else:
            return int(s)
    
    def update_argparser(self, argparser, *, with_help=True):
        argname = self.name.replace('_', '-')
        
        if with_help:
            docstring = '{} (default: {})'.format(
                self.docstring, self.default_str)
        else:
            docstring = argparse.SUPPRESS
        
        argparser.add_argument('--' + argname,
                               help=docstring,
                               action='store',
                               dest=self.name)


class TypedefConfigAttribute(BaseConfigAttribute):
    
    def __init__(self, name, default_str, docstring):
        super().__init__(name, default_str, docstring)
    
    def parse(self, s):
        return parse_typedef(s)
    
    def update_argparser(self, argparser, *, with_help=True):
        argname = self.name.replace('_', '-')
        
        if with_help:
            docstring = self.docstring
        else:
            docstring = argparse.SUPPRESS
        
        argparser.add_argument('--' + argname,
                               help=docstring,
                               action='store',
                               dest=self.name)


all_attributes = [
    BooleanConfigAttribute('verbose', 'false',
        'print transformation information to standard output'),
    
    BooleanConfigAttribute('pretend', 'false',
        'write to standard output instead of the output file'),
    
    BooleanConfigAttribute('obj_domain', 'false',
        'flatten sets and objects'),
    
    EnumConfigAttribute('default_impl', 'normal',
        'default implementation strategy to use for queries',
        ['normal', 'aux', 'inc', 'filtered']),
    
    IntNoneConfigAttribute('default_demand_set_maxsize', 'none',
        'default value of demand_set_maxsize to use for all queries'),
    
    BooleanConfigAttribute('use_singletag_demand', 'false',
        'only use one tag in the definition of each filter'),
    
    BooleanConfigAttribute('unwrap_singletons', 'false',
        'rewrite singleton relations to eliminate unneeded tuples'),
    
    BooleanConfigAttribute('auto_query', 'false',
        'automatically consider comps/aggrs as queries even without '
        'QUERY annotations'),
    
    BooleanConfigAttribute('inline_maint_code', 'false',
        'inline inserted maintenance functions'),
    
    BooleanConfigAttribute('elim_counts', 'true',
        'eliminate counts where we can infer it\'s safe to do so'),
    
    BooleanConfigAttribute('elim_dead_relations', 'true',
        'eliminate dead relations'),
    
    BooleanConfigAttribute('elim_type_checks', 'true',
        'eliminate type checks where safe'),
    
    BooleanConfigAttribute('elim_dead_funcs', 'true',
        'eliminate uncalled maintenance functions'),
    
    BooleanConfigAttribute('distalgo_mode', 'true',
        'enable special rewritings for DistAlgo inc interface'),
    
    TypedefConfigAttribute('typedefs', '',
        'mapping from type identifiers to type definition, in form of '
        '"name=typeexpr; ...; name=typeexpr" declarations'),
    
    BooleanConfigAttribute('costs', 'true',
        'emit cost annotation comments at the top of functions'),
]


class Config:
    
    """A bundle of configuration attributes."""
    
    # Attribute descriptors are pulled in from all_attributes
    # programmatically. (Beware if subclassing Config.)
    
    def __str__(self):
        return '\n'.join('{}: {}'.format(attr.name, getattr(self, attr.name))
                         for attr in all_attributes)
    
    def parse_and_update(self, **kargs):
        """Given the string-to-string mapping specified by **kargs,
        update all stored attributes to their parsed values. Attribute
        keys that are missing from **kargs or that map to None are
        ignored, i.e., their previous value is left standing.
        """
        for attr, value in kargs.items():
            if value is None:
                continue
            
            descriptor = getattr(type(self), attr, None)
            if not isinstance(descriptor, BaseConfigAttribute):
                raise ValueError('Unknown config attribute "{}"'.format(attr))
            
            value = descriptor.parse(value)
            setattr(self, attr, value)

for attr in all_attributes:
    setattr(Config, attr.name, attr)


def get_argparser(*, with_help=True):
    """Return a parent parser for the configuration options."""
    argparser = argparse.ArgumentParser(add_help=False)
    for attr in all_attributes:
        attr.update_argparser(argparser, with_help=with_help)
    return argparser


def extract_options(namespace):
    """Given an argument parser namespace, return an options dictionary
    for all configuration options.
    """
    return {attr.name: getattr(namespace, attr.name)
            for attr in all_attributes
            if getattr(namespace, attr.name) is not None}
