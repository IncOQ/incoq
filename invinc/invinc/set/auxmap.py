"""Auxiliary maps over relations."""

# WISHLIST: Add an analysis to determine when it's safe to use the
# update element components directly, and either avoid generating
# the assignment to the v vars, or else remove it with a later
# processing step.


__all__ = [
    'AuxmapMaintainer',
    'inc_relmatch',
    'RelmatchQueryFinder',
    'DeltaMatchRewriter',
    'inc_all_relmatch',
]


from util.collections import OrderedSet
import invinc.incast as L

from .mask import Mask, AuxmapSpec


def get_relmatch(node):
    id, mask, key = L.get_namematch(node)
    return AuxmapSpec(id, Mask(mask)), key

is_relmatch = L.is_namematch

def get_relsmlookup(node):
    id, mask, key = L.get_namesmlookup(node)
    return AuxmapSpec(id, Mask(mask)), key

is_relsmlookup = L.is_namesmlookup


def make_vareq_cond(eqs):
    """Given a list of pairs of variables, return a conjunction of
    equalities, one for each pair.
    """
    eqcond = L.BoolOp(L.And(), tuple(L.cmpeq(L.ln(v1), L.ln(v2))
                                     for v1, v2 in eqs))
    return eqcond


def make_auxmap_maint_code(manager, spec, elem, addremove):
    """Construct auxmap maintenance code for a set update."""
    assert addremove in ['add', 'remove']
    
    prefix = manager.namegen.next_prefix()
    mask = spec.mask
    
    # Create fresh variables for the tuple components.
    vars = [prefix + str(i) for i in range(1, len(mask) + 1)]
    bvars, uvars, eqs = mask.split_vars(vars)
    
    vars_node = L.tuplify(vars, lval=True)
    map_node = L.ln(spec.map_name)
    bvars_node = L.tuplify(bvars)
    uvars_node = L.tuplify(uvars)
    
    # If there are equalities, include a conditional check for the
    # constraints being satisfied. If there are wildcards, make the
    # image set manipulation operations reference-counted.
    #
    # Avoid these in cases where we don't have equalities/wildcards,
    # to help reduce constant-factor bloat in code size and running
    # time.
    
    if mask.has_equalities:
        template = '''
            VARS = ELEM
            if EQCOND:
                MAP.IMGOP(BVARS, UVARS)
            '''
        eqcond = make_vareq_cond(eqs)
    else:
        template = '''
            VARS = ELEM
            MAP.IMGOP(BVARS, UVARS)
            '''
        eqcond = None
    
    if mask.has_wildcards:
        imgop = {'add': 'rcimgadd',
                 'remove': 'rcimgremove'}[addremove]
    else:
        imgop = {'add': 'imgadd',
                 'remove': 'imgremove'}[addremove]
    
    code = L.pc(template, subst={
        '@IMGOP': imgop,
        'VARS': vars_node,
        'ELEM': elem,
        'MAP': map_node,
        'BVARS': bvars_node,
        'UVARS': uvars_node,
        'EQCOND': eqcond})
    
    return code


class AuxmapMaintainer(L.NodeTransformer):
    
    """Auxiliary map maintenance transformer."""
    
    def __init__(self, manager, spec):
        super().__init__()
        self.manager = manager
        self.spec = spec
        
        mapname = self.spec.map_name
        self.addfunc_name = '_maint_{}_add'.format(mapname)
        self.removefunc_name = '_maint_{}_remove'.format(mapname)
    
    def visit_Module(self, node):
        mapname = self.spec.map_name
        addcode = make_auxmap_maint_code(self.manager, self.spec,
                                         L.ln('_e'), 'add')
        removecode = make_auxmap_maint_code(self.manager, self.spec,
                                            L.ln('_e'), 'remove')
        
        code = L.pc('''
            MAP = Map()
            def ADDFUNC(_e):
                ADDCODE
            def REMOVEFUNC(_e):
                REMOVECODE
            ''', subst={'MAP': L.sn(mapname),
                        '<def>ADDFUNC': self.addfunc_name,
                        '<c>ADDCODE': addcode,
                        '<def>REMOVEFUNC': self.removefunc_name,
                        '<c>REMOVECODE': removecode})
        
        node = node._replace(body=code + node.body)
        
        node = self.generic_visit(node)
        
        return node
    
    def visit_SetUpdate(self, node):
        node = self.generic_visit(node)
        
        # No action if
        #  - this is not an update to a variable
        #  - this is not the variable you are looking for (jedi hand wave)
        if not node.is_varupdate():
            return node
        var, op, elem = node.get_varupdate()
        if var != self.spec.rel:
            return node
        
        precode = postcode = ()
        if op == 'add':
            postcode = L.pc('ADDFUNC(ELEM)',
                            subst={'ADDFUNC': self.addfunc_name,
                                   'ELEM': elem})
        elif op == 'remove':
            precode = L.pc('REMOVEFUNC(ELEM)',
                            subst={'REMOVEFUNC': self.removefunc_name,
                                   'ELEM': elem})
        else:
            assert()
        
        code = L.Maintenance(self.spec.map_name, L.ts(node),
                             precode, (node,), postcode)
        return code


class MapqueryReplacer(L.NodeTransformer):
    
    """Replace relmatch and smlookup queries with uses of the
    corresponding auxmap.
    """
    
    def __init__(self, manager, spec):
        super().__init__()
        self.manager = manager
        self.spec = spec
    
    def visit_SetMatch(self, node):
        node = self.generic_visit(node)
        
        if not is_relmatch(node):
            return node
        spec, bounds = get_relmatch(node)
        
        if spec != self.spec:
            return node
        
        lookup = ('rcimglookup' if self.spec.mask.has_wildcards
                  else 'imglookup')
        
        code = L.pe('''
            MAP.LOOKUP(BOUNDS)
            ''', subst={'MAP': L.ln(self.spec.map_name),
                        'BOUNDS': bounds,
                        '@LOOKUP': lookup})
        return code
    
    def visit_SMLookup(self, node):
        node = self.generic_visit(node)
        
        if not is_relsmlookup(node):
            return node
        spec, key = get_relsmlookup(node)
        
        if spec != self.spec:
            return node
        
        if node.default is not None:
            code = L.pe('''
                MAP.singlelookup(KEY, DEFAULT)
                ''', subst={'MAP': L.ln(self.spec.map_name),
                            'KEY': key,
                            'DEFAULT': node.default})
        else:
            code = L.pe('''
                MAP.singlelookup(KEY)
                ''', subst={'MAP': L.ln(self.spec.map_name),
                            'KEY': key})
        
        return code


def inc_relmatch(tree, manager, spec):
    """Incrementalize a relmatch query / SMLookup."""
    if manager.options.get_opt('verbose'):
        print('Adding auxmap: ' + str(spec))
    
    tree = MapqueryReplacer.run(tree, manager, spec)
    tree = AuxmapMaintainer.run(tree, manager, spec)
    
    return tree


class RelmatchQueryFinder(L.NodeVisitor):
    
    """Return the set of auxmap specs that are used by some
    relmatch query or set-map lookup.
    """
    
    def process(self, tree):
        self.specs = OrderedSet()
        super().process(tree)
        return self.specs
    
    def visit_SetMatch(self, node):
        self.generic_visit(node)
        
        if is_relmatch(node):
            spec, _key = get_relmatch(node)
            self.specs.add(spec)
    
    def visit_SMLookup(self, node):
        self.generic_visit(node)
        
        if is_relsmlookup(node):
            spec, _key = get_relsmlookup(node)
            self.specs.add(spec)


class DeltaMatchRewriter(L.NodeTransformer):
    
    """Replace DeltaMatch nodes with equivalent SetMatch-based code."""
    
    def visit_DeltaMatch(self, node):
        mask = Mask(node.mask)
        
        if mask.has_wildcards:
            key = mask.make_projkey(node.elem)
            return L.pe('''
                ({ELEM} if setmatch(TARGET, MASK, KEY).getref(()) == LIMIT
                        else {})
                ''', subst={'ELEM': node.elem,
                            'TARGET': node.target,
                            'MASK': mask.make_node(),
                            'KEY': key,
                            'LIMIT': L.Num(node.limit)})
        
        elif mask.has_equalities:
            # FIXME: Not sure how to handle this right now.
            assert()
        
        else:
            return L.pe('{ELEM}', subst={'ELEM': node.elem})


def inc_all_relmatch(tree, manager):
    """Incrementalize all setmatch and smlookup queries."""
    tree = DeltaMatchRewriter.run(tree)
    specs = RelmatchQueryFinder.run(tree)
    for spec in specs:
        tree = inc_relmatch(tree, manager, spec)
        manager.stats['auxmaps'] += 1
    return tree
