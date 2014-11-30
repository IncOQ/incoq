###############################################################################
# type.py                                                                     #
# Author: Jon Brandvein                                                       #
###############################################################################

"""Utilities for facilitating type checking."""

# Spare me the "It's not the Python way" lectures. I've lost too much
# time to type errors in this code base.

# In the future, this might be replaceable by a library that does type
# checking based on function annotations.

# TODO: See if I can make exceptions exclude the innermost stack
# frame(s) so it appears the errors are being raised where I want them
# to.


__all__ = [
    'checktype',
    'checktype_seq',
    'checksubclass',
    'checksubclass_seq',
    
    'TypeCase',
]


def strval(val):
    """Helper for error messages."""
    if isinstance(val, type):
        return val.__name__ + ' class'
    else:
        return type(val).__name__ + ' object'

def checktype(val, typ):
    """Raise TypeError if val is not of type typ."""
    if not isinstance(val, typ):
        exp = typ.__name__
        got = strval(val)
        raise TypeError('Expected {}; got {}'.format(exp, got))

def checktype_seq(seq, typ):
    """Raise TypeError if any element of seq is not of type typ.
    
    As a special case, a string does not count as a sequence of strings
    (to catch a common error case). 
    """
    exp = typ.__name__
    
    # Make sure we have a sequence.
    try:
        iterator = iter(seq)
        # Generators aren't sequences. This avoids a confusing case
        # where we consume a generator by type-checking it, and leave
        # only an exhausted iterator for the user code.
        len(seq)
    except (TypeError, AssertionError):
        got = strval(seq)
        raise TypeError('Expected sequence of {}; '
                        'got {} instead of sequence'.format(exp, got))
    
    if typ is str:
        if isinstance(seq, str):
            raise TypeError('Expected non-string sequence of str; '
                            'got string')
        
    for item in iterator:
        if not isinstance(item, typ):
            got = strval(item)
            raise TypeError('Expected sequence of {}; '
                            'got sequence with {}'.format(exp, got))

def checksubclass(val, cls):
    """Raise TypeError if val is not a subclass of cls."""
    if not isinstance(val, type) or not issubclass(val, cls):
        exp = cls.__name__
        got = strval(val)
        raise TypeError('Expected subclass of {}; got {}'.format(exp, got))

def checksubclass_seq(seq, cls):
    """Raise TypeError if any element of seq is not a subclass of cls."""
    exp = cls.__name__
    
    try:
        iterator = iter(seq)
    except TypeError:
        got = strval(seq)
        raise TypeError('Expected sequence of subclasses of {}; '
                        'got {} instead of sequence'.format(exp, got))
    
    for item in iterator:
        if not isinstance(item, type) or not issubclass(item, cls):
            got = strval(item)
            raise TypeError('Expected sequence of subclasses of {}; '
                            'got sequence with {}'.format(exp, got))


class TypeCase:
    
    """Mixin for unittest."""
    
    def assertTypeError(self, expected, sequence=False, subclass=False):
        exp_words = ['Expected',
                     'sequence' if sequence else '',
                     'subclass' if subclass else '',
                     expected.__name__,
                     'got']
        exp_msg = '.*'.join(exp_words)
        
        return self.assertRaisesRegex(TypeError, exp_msg)
