"""Configuration management."""


__all__ = [
    'ConfigAttribute',
    'Config',
]


from simplestruct import Struct, Field


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
    
    ConfigAttribute('unwrap_singletons', False,
        'rewrite singleton relations to eliminate unneeded tuples',
        {'action': 'store_true'})
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
