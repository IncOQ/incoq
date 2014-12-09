"""Pair-relation match operations."""


__all__ = [
    'mset_bindmatch',
    'fset_bindmatch',
    'mapset_bindmatch',
]


import oinc.incast as L
from oinc.set import Mask

from .pairrel import make_maprel


def mset_bindmatch(mask, bvars, uvars, body, *, typecheck):
    """Form code for bindmatch over the M-set."""
    
    tc_applicable = False
    
    if mask == Mask.BB:
        tc_applicable = True
        cont, item = bvars
        code = L.pc('''
            if ITEM in CONT:
                BODY
            ''', subst={'CONT': L.ln(cont),
                        'ITEM': L.ln(item),
                        '<c>BODY': body})
    
    elif mask == Mask.OUT:
        tc_applicable = True
        (cont,) = bvars
        (item,) = uvars
        code = L.pc('''
            for ITEM in CONT:
                BODY
            ''', subst={'CONT': L.ln(cont),
                        'ITEM': L.sn(item),
                        '<c>BODY': body})
    
    elif mask == Mask.B1:
        tc_applicable = True
        (cont,) = (item,) = bvars
        code = L.pc('''
            if CONT in CONT:
                BODY
            ''', subst={'CONT': L.ln(cont),
                        '<c>BODY': body})
    
    elif mask == Mask.BW:
        tc_applicable = True
        (cont,) = bvars
        code = L.pc('''
            if not CONT.isempty():
                BODY
            ''', subst={'CONT': L.ln(cont),
                        '<c>BODY': body})
    
    elif mask == Mask.UU:
        raise AssertionError('No object-domain equivalent for iterating over '
                             'the M-set')
    
    else:
        code = L.pc('''
            for UVARS in setmatch(SET, MASK, BVARS):
                BODY
            ''', subst={'UVARS': L.tuplify(uvars, lval=True),
                        'SET': L.ln('_M'),
                        'MASK': mask.make_node(),
                        'BVARS': L.tuplify(bvars),
                        '<c>BODY': body})
    
    if typecheck and tc_applicable:
        code = L.pc('''
            if isinstance(CONT, Set):
                CODE
            ''', subst={'CONT': cont,
                        '<c>CODE': code})
    
    return code


def fset_bindmatch(field, mask, bvars, uvars, body, *, typecheck):
    """Form code for bindmatch over an F-set."""
    
    # If we had such a thing as a negated field membership clause,
    # then the negative test for hasattr() would actually conflict
    # with the type check.
    
    tc_applicable = False
    
    if mask == Mask.BB:
        tc_applicable = True
        cont, item = bvars
        code = L.pc('''
            if CONT.FIELD == ITEM:
                BODY
            ''', subst={'CONT': L.ln(cont),
                        '@FIELD': field,
                        'ITEM': L.ln(item),
                        '<c>BODY': body})
    
    elif mask == Mask.OUT:
        tc_applicable = True
        (cont,) = bvars
        (item,) = uvars
        code = L.pc('''
            ITEM = CONT.FIELD
            BODY
            ''', subst={'CONT': L.ln(cont),
                        '@FIELD': field,
                        'ITEM': L.sn(item),
                        '<c>BODY': body})
    
    elif mask == Mask.B1:
        tc_applicable = True
        (cont,) = (item,) = bvars
        code = L.pc('''
            if CONT == CONT.FIELD:
                BODY
            ''', subst={'CONT': L.ln(cont),
                        '@FIELD': field,
                        '<c>BODY': body})
    
    elif mask == Mask.BW:
        # Not applicable because the code and the type check
        # are the same thing.
        tc_applicable = False
        (cont,) = bvars
        code = L.pc('''
            if hasattr(CONT, FIELD):
                BODY
            ''', subst={'CONT': L.ln(cont),
                        'FIELD': L.Str(field),
                        '<c>BODY': body})
    
    elif mask == Mask.UU:
        raise AssertionError('No object-domain equivalent for iterating over '
                             'the M-set')
    
    else:
        code = L.pc('''
            for UVARS in setmatch(SET, MASK, BVARS):
                BODY
            ''', subst={'UVARS': L.tuplify(uvars, lval=True),
                        'SET': L.ln('_F_' + field),
                        'MASK': mask.make_node(),
                        'BVARS': L.tuplify(bvars),
                        '<c>BODY': body})
    
    if typecheck and tc_applicable:
        code = L.pc('''
            if hasattr(CONT, FIELD):
                CODE
            ''', subst={'CONT': cont,
                        'FIELD': L.Str(field),
                        '<c>CODE': code})
    
    return code


def mapset_bindmatch(mask, bvars, uvars, body, *, typecheck):
    """Form code for bindmatch over the MAP set."""
    
    tc_applicable = False
    
    if mask == Mask('bbb'):
        tc_applicable = True
        map, key, value = bvars
        code = L.pc('''
            if KEY in MAP and MAP[KEY] == VALUE:
                BODY
            ''', subst={'MAP': L.ln(map),
                        'KEY': L.ln(key),
                        'VALUE': L.ln(value),
                        '<c>BODY': body})
    
    elif mask == Mask('bbu'):
        tc_applicable = True
        map, key = bvars
        (value,) = uvars
        code = L.pc('''
            if KEY in MAP:
                VALUE = MAP[KEY]
                BODY
            ''', subst={'MAP': L.ln(map),
                        'KEY': L.ln(key),
                        'VALUE': L.sn(value),
                        '<c>BODY': body})
    
    elif mask == Mask('buu'):
        tc_applicable = True
        (map,) = bvars
        key, value = uvars
        code = L.pc('''
            for KEY, VALUE in MAP.items():
                BODY
            ''', subst={'MAP': L.ln(map),
                        'KEY': L.sn(key),
                        'VALUE': L.sn(value),
                        '<c>BODY': body})
    
    # Other variations involving wildcards and equalities are possible,
    # but for now they're handled by the general auxmap case.
    
    elif mask == Mask('uuu'):
        raise AssertionError('No object-domain equivalent for iterating over '
                             'the MAP set')
    
    else:
        code = L.pc('''
            for UVARS in setmatch(SET, MASK, BVARS):
                BODY
            ''', subst={'UVARS': L.tuplify(uvars, lval=True),
                        'SET': L.ln(make_maprel()),
                        'MASK': mask.make_node(),
                        'BVARS': L.tuplify(bvars),
                        '<c>BODY': body})
    
    if typecheck and tc_applicable:
        code = L.pc('''
            if isinstance(MAP, Map):
                CODE
            ''', subst={'MAP': map,
                        '<c>CODE': code})
    
    return code
