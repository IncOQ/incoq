"""Common utilities."""


__all__ = [
    'parse_bool',
    'parse_list',
    'ParseableEnumMixin',
]


def parse_bool(s):
    s = s.lower()
    if s == 'true':
        return True
    elif s == 'false':
        return False
    else:
        raise ValueError('Bad attribute value')


def parse_list(s):
    result = s.split(',')
    result = [it.strip() for it in result]
    return result


class ParseableEnumMixin:
    
    """Mixin for Enums that have a parse() method for converting from
    string representations.
    """
    
    @classmethod
    def parse(cls, s):
        d = {k.lower(): v for k, v in cls.__members__.items()}
        if s in d:
            return d[s]
        else:
            raise ValueError('Bad attribute value')