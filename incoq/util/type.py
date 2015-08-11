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
    
    'typechecked',
]


from functools import wraps
from inspect import signature, Parameter, Signature


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


def typechecked(func):
    sig = signature(func)
    
    for param_name, param in sig.parameters.items():
        ann = param.annotation
        if ann == Parameter.empty:
            continue
        if not isinstance(ann, type):
            raise TypeError('Bad annotation for parameter "{}": {}'.format(
                            param_name, ann))
    ann = sig.return_annotation
    if ann != Signature.empty:
        if not isinstance(ann, type):
            raise TypeError('Bad annotation for return: {}'.format(
                            ann))
    
    @wraps(func)
    def wrapper(*args, **kargs):
        boundargs = sig.bind(*args, **kargs)
        for param, value in boundargs.arguments.items():
            ann = sig.parameters[param].annotation
            if ann != Parameter.empty:
                if not isinstance(value, ann):
                    raise TypeError('Value for parameter "{}" does not match '
                                    'type annotation: expected {}, '
                                    'got {}'.format(
                                    param, ann.__name__,
                                    value.__class__.__name__))
        
        result = func(*args, **kargs)
        
        ann = sig.return_annotation
        if ann != Signature.empty:
            if not isinstance(result, ann):
                raise TypeError('Return value does not match type '
                                'annotation: expected {}, got {}'.format(
                                ann.__name__, result.__class__.__name__))
        
        return result
    
    return wrapper
