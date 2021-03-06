"""Tuple relations."""


__all__ = [
    'is_trel',
    'get_trel',
    'make_trel',
    
    'trel_bindmatch',
    'check_bad_setmatches',
]


import incoq.compiler.incast as L


def is_trel(rel):
    return rel.startswith('_TUP')

def get_trel(rel):
    assert rel.startswith('_TUP')
    arity = rel[len('_TUP'):]
    return int(arity)

def make_trel(arity):
    return '_TUP' + str(arity)


def trel_bindmatch(trel, mask, vars, body, *, typecheck):
    """Make code to pattern match over a tuple relation."""
    assert len(mask) >= 2
    tup, *elts = vars
    arity = get_trel(trel)
    assert arity == len(elts)
    bvars, uvars, _eqs = mask.split_vars(vars)
    
    if mask.parts[0] == 'b':
        # Kick it over to setmatch(). The set being matched is
        # a singleton containing a tuple whose first component
        # is the passed-in tuple, and whose remaining components
        # are those of the passed-in tuple, i.e.
        #
        #    (tup, tup[0], ..., tup[n])
        #
        # This allows the mask to work correctly with arbitrary
        # equality components, wildcards, etc.
        singtup_elts = (L.ln(tup),)
        for i in range(arity):
            singtup_elts += (L.pe('TUP[IND]', subst={'TUP': L.ln(tup),
                                                     'IND': L.Num(i)}),)
        singtup = L.Tuple(singtup_elts, L.Load())
        
        code = L.pc('''
            for UVARS in setmatch({SINGTUP}, MASK, BVARS):
                BODY
            ''', subst={'UVARS': L.tuplify(uvars, lval=True),
                        'SINGTUP': singtup,
                        'MASK': mask.make_node(),
                        'BVARS': L.tuplify(bvars),
                        '<c>BODY': body})
        
        # If any other part of the mask besides the first component
        # is bound, we need to confirm that it is consistent with
        # the tuple value of the first component.
        var_parts = list(enumerate(zip(vars, mask.parts)))
        conds = [L.pe('TUP[IND] == VAR', subst={'TUP': L.ln(tup),
                                                'IND': L.Num(i),
                                                'VAR': L.ln(var)})
                 for i, (var, part) in var_parts
                 if i > 0 if part == 'b']
        if len(conds) == 0:
            cond = None
        elif len(conds) == 1:
            cond = conds[0]
        else:
            cond = L.BoolOp(L.And(), conds)
        if cond is not None:
            code = L.pc('''
                if COND:
                    CODE
                ''', subst={'COND': cond,
                            '<c>CODE': code})
        
        if typecheck:
            code = L.pc('''
                if isinstance(TUP, tuple) and len(TUP) == ARITY:
                    CODE
                ''', subst={'TUP': L.ln(tup),
                            'ARITY': L.Num(arity),
                            '<c>CODE': code})
    
    # TODO: Case where first component is unbound but all other
    # components are bound, in which case we can avoid a map lookup.
    
    else:
        code = L.pc('''
            for UVARS in setmatch(SET, MASK, BVARS):
                BODY
            ''', subst={'UVARS': L.tuplify(uvars, lval=True),
                        'SET': L.ln(trel),
                        'MASK': mask.make_node(),
                        'BVARS': L.tuplify(bvars),
                        '<c>BODY': body})
    
    return code


def check_bad_setmatches(tree):
    """Raise an error if there are any setmatches over tuple relations,
    which are not meaningful in the final program since tuple relations
    are not materialized.
    """
    class Vis(L.NodeVisitor):
        def visit_SetMatch(self, node):
            if (isinstance(node.target, L.Name) and
                is_trel(node.target.id)):
                raise AssertionError('Cannot generate general auxiliary map '
                                     'over nested tuples without using '
                                     'demand')
    Vis.run(tree)
