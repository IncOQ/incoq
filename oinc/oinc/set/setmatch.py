###############################################################################
# setmatch.py                                                                 #
# Author: Jon Brandvein                                                       #
###############################################################################

"""Tuple pattern matching."""


__all__ = [
    'make_bindmatch',
    'make_tuplematch',
]


import oinc.incast as L


def make_bindmatch(rel, mask, bvars, uvars, body):
    if mask.is_allbound and not mask.has_equalities:
        template = L.trim('''
            if BVARS in REL:
                BODY
            ''')
    
    elif mask.is_allunbound and not mask.has_wildcards:
        template = L.trim('''
            for UVARS in REL:
                BODY
            ''')
    
    else:
        template = L.trim('''
            for UVARS in setmatch(REL, MASK, BVARS):
                BODY
            ''')
    
    code = L.pc(template, subst={'REL': L.ln(rel),
                                 'MASK': mask.make_node(),
                                 'BVARS': L.tuplify(bvars),
                                 'UVARS': L.tuplify(uvars, lval=True),
                                 '<c>BODY': body})
    return code


def make_tuplematch(val, mask, bvars, uvars, body):
    if mask.is_allbound:
        template = L.trim('''
            if BVARS == VAL:
                BODY
            ''')
    
    elif mask.is_allunbound and not mask.has_wildcards:
        template = L.trim('''
            UVARS = VAL
            BODY
            ''')
    
    else:
        template = L.trim('''
            for UVARS in setmatch({VAL}, MASK, BVARS):
                BODY
            ''')
    
    code = L.pc(template,
                subst={'VAL': val,
                       'MASK': mask.make_node(),
                       'BVARS': L.tuplify(bvars),
                       'UVARS': L.tuplify(uvars, lval=True),
                       '<c>BODY': body})
    return code
