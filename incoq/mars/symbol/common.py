"""Common utilities."""


__all__ = [
    'parse_bool',
    'parse_list',
    'parse_int_list',
    'ParseableEnumMixin',
]


def parse_bool(s, symtab=None):
    s = s.lower()
    if s == 'true':
        return True
    elif s == 'false':
        return False
    else:
        raise ValueError('Bad attribute value')


def parse_list(s, symtab=None):
    result = s.split(',')
    result = [it.strip() for it in result]
    return result

def parse_int_list(s, symtab=None):
    result = s.split(',')
    result = [int(it.strip()) for it in result]
    return result


class ParseableEnumMixin:
    
    """Mixin for Enums that have a parse() method for converting from
    string representations.
    """
    
    @classmethod
    def parse(cls, s, symtab=None):
        d = {k.lower(): v for k, v in cls.__members__.items()}
        if s in d:
            return d[s]
        else:
            raise ValueError('Bad attribute value')
