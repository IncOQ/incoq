"""Miscellaneous utilities."""


__all__ = [
    'flood_namespace',
    'new_namespace',
    
    'freeze',
]


from types import ModuleType, SimpleNamespace

from .collections import frozendict


def flood_namespace(target, *sources):
    """Given a target namespace and other source namespaces,
    copy each source into the target.
    
    If a Module is passed as a source namespace, its __dict__
    is used.
    
    If a namespace supplies an '__all__' key, only entries listed
    in '__all__' are used. Otherwise, only entries not starting
    with an underscore are used. This mirrors the semantics of
    from ... import *.
    
    If the target namespace defines an '__all__' key, it is
    updated to include the names of the copied keys.
    
    The sources are assumed to be disjoint.
    """
    for ns in sources:
        if isinstance(ns, ModuleType):
            ns = ns.__dict__
        
        if '__all__' in ns:
            # Make sure to preserve the order of __all__.
            keys = ns['__all__']
            ns = [(k, ns[k]) for k in ns['__all__']]
        else:
            ns = {k: v for k, v in ns.items() if not k.startswith('_')}
            keys = ns.keys()
        
        target.update(ns)
        if '__all__' in target:
            target['__all__'].extend(keys)


def new_namespace(*sources):
    """As above but make a new target namespace, using SimpleNamespace."""
    ns = {}
    flood_namespace(ns, *sources)
    return SimpleNamespace(**ns)


def freeze(value):
    """Return a frozen version of the given value, which may be composed
    of lists, sets, dictionaries, tuples, and primitive immutable
    non-collection types. The frozen version replaces lists with tuples,
    sets with frozensets, and dicts with frozendicts.
    """
    if isinstance(value, list):
        value = tuple(freeze(e) for e in value)
    elif isinstance(value, set):
        value = frozenset(freeze(e) for e in value)
    elif isinstance(value, dict):
        value = frozendict({k: freeze(v) for k, v in value.items()})
    elif isinstance(value, tuple):
        value = tuple(freeze(e) for e in value)
    else:
        pass
    return value
