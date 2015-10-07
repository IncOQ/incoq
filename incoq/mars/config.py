"""Configuration management."""


__all__ = [
    'Attribute',
    'Config',
]


from simplestruct import Struct, Field


# Each configuration attribute is a descriptor, listed in the
# all_attributes list, and put in the class namespace for Config.
# The order of all_attributes is canonical for user documentation
# purposes.


class Attribute(Struct):
    
    """Descriptor for a configuration attribute."""
    
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
        else:
            return getattr(inst, '_' + self.name, self.default)
    
    def __set__(self, inst, value):
        setattr(inst, '_' + self.name, value)


all_attributes = [
    Attribute('verbose', False,
              'print transformation information to standard output',
              {'action': 'store_true'}),
    
    Attribute('unwrap_singletons', False,
              'rewrite singleton relations to eliminate unneeded tuples',
              {'action': 'store_true'})
]


class Config:
    
    """A bundle of configuration attributes."""
    
    # Attribute descriptors are pulled in from all_attributes
    # programmatically. Methods refer to all_attributes, so
    # any subclasses of Config may have problems.
    
    def __str__(self):
        return '\n'.join('{}: {}'.format(attr.name, getattr(self, attr.name))
                         for attr in all_attributes)
    
    def update(self, **kargs):
        for attr, value in kargs.items():
            if not isinstance(getattr(type(self), attr, None), Attribute):
                raise ValueError('Unknown config attribute "{}"'.format(attr))
            setattr(self, attr, value)

for attr in all_attributes:
    setattr(Config, attr.name, attr)
