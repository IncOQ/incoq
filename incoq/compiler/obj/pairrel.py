"""Special relations used for object-domain translation."""


__all__ = [
    'MREL_NAME',
    'FREL_PREFIX',
    'MAPREL_NAME',
    'make_mrel',
    'make_frel',
    'make_maprel',
    'is_mrel',
    'is_frel',
    'is_maprel',
    'is_specialrel',
    'get_frel_field',
    
    'get_menum',
    'is_menum',
    'get_fenum',
    'is_menum',
    'get_mapenum',
    'is_mapenum',
]


import incoq.compiler.incast as L


MREL_NAME = '_M'
FREL_PREFIX = '_F_'
MAPREL_NAME = '_MAP'


def make_mrel():
    return MREL_NAME

def make_frel(field):
    return FREL_PREFIX + field

def make_maprel():
    return MAPREL_NAME

def is_mrel(rel):
    return rel == MREL_NAME

def is_frel(rel):
    return rel.startswith(FREL_PREFIX)

def is_maprel(rel):
    return rel == MAPREL_NAME

def is_specialrel(rel):
    return is_mrel(rel) or is_frel(rel) or is_maprel(rel)

def get_frel_field(rel):
    assert rel.startswith(FREL_PREFIX)
    return rel[len(FREL_PREFIX):]


# The following functions take in a comprehension clause (possibly a
# condition clause), and return the parsed information if it has
# the right form, or None if it does not. It is an error if the clause
# is an enumerator over a special relation but doesn't have the correct
# arity on its left-hand side.

def get_menum(cl):
    """Parse a membership clause, returning the set and element
    components.
    """
    if not (isinstance(cl, L.Enumerator) and
            isinstance(cl.iter, L.Name) and
            is_mrel(cl.iter.id)):
        return None
    assert isinstance(cl.target, L.Tuple) and len(cl.target.elts) == 2
    return cl.target.elts

def is_menum(cl):
    return get_menum(cl) is not None

def get_fenum(cl):
    """Parse a field clause, returning a triple of the object component,
    value component, and field name.
    """
    if not (isinstance(cl, L.Enumerator) and
            isinstance(cl.iter, L.Name) and
            is_frel(cl.iter.id)):
        return None
    assert isinstance(cl.target, L.Tuple) and len(cl.target.elts) == 2
    obj, value = cl.target.elts
    field = get_frel_field(cl.iter.id)
    return obj, value, field

def is_fenum(cl):
    return get_fenum(cl) is not None

def get_mapenum(cl):
    """Parse a map clause, returning a triple of the map, key, and
    value components.
    """
    if not (isinstance(cl, L.Enumerator) and
            isinstance(cl.iter, L.Name) and
            is_maprel(cl.iter.id)):
        return None
    assert isinstance(cl.target, L.Tuple) and len(cl.target.elts) == 3
    return cl.target.elts

def is_mapenum(cl):
    return get_mapenum(cl) is not None
