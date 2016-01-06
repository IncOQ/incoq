"""Auxiliary map transformation."""


__all__ = [
    'AuxmapInvariant',
    'AuxmapFinder',
    'AuxmapTransformer',
    'make_auxmap_type',
    'define_map',
]


from collections import OrderedDict
from simplestruct import Struct, TypedField

from incoq.util.collections import OrderedSet
from incoq.util.type import typechecked
from incoq.mars.incast import L
import incoq.mars.types as T
from incoq.mars.symtab import N


class AuxmapInvariant(Struct):
    
    """Auxiliary map invariant."""
    
    map = TypedField(str)
    """Name of variable holding the map."""
    rel = TypedField(str)
    """Name of relation being indexed."""
    mask = TypedField(L.mask)
    """Mask for the indexing."""
    
    def get_maint_func_name(self, op):
        op_name = L.set_update_name(op)
        return N.get_maint_func_name(self.map, self.rel, op_name)


@typechecked
def make_imgadd(fresh_vars, target: str, key: str, elem: str):
    """Make code to add elem to the image set for key in target."""
    var = next(fresh_vars)
    return L.Parser.pc('''
        if _KEY not in _TARGET:
            _VAR = Set()
            _TARGET.mapassign(_KEY, _VAR)
        _TARGET[_KEY].add(_ELEM)
        ''', subst={'_TARGET': target,
                    '_KEY': key,
                    '_ELEM': elem,
                    '_VAR': var})


@typechecked
def make_imgremove(fresh_vars, target: str, key: str, elem: str):
    """Make code to remove elem from the image set for key in target."""
    return L.Parser.pc('''
        _TARGET[_KEY].remove(_ELEM)
        if len(_TARGET[_KEY]) == 0:
            _TARGET.mapdelete(_KEY)
        ''', subst={'_TARGET': target,
                    '_KEY': key,
                    '_ELEM': elem})


@typechecked
def make_auxmap_maint_func(fresh_vars,
                           auxmap: AuxmapInvariant, op: L.setupop):
    """Make maintenance function for auxiliary map."""
    # Fresh variables for components of the element.
    vars = N.get_subnames('_elem', len(auxmap.mask.m))
    
    decomp_code = (L.DecompAssign(vars, L.Name('_elem')),)
    
    key, value = L.split_by_mask(auxmap.mask, vars)
    key = L.tuplify(key)
    value = L.tuplify(value)
    fresh_var_prefix = next(fresh_vars)
    key_var = fresh_var_prefix + '_key'
    value_var = fresh_var_prefix + '_value'
    
    decomp_code += L.Parser.pc('''
        _KEY_VAR = _KEY
        _VALUE_VAR = _VALUE
        ''', subst={'_KEY_VAR': key_var, '_KEY': key,
                    '_VALUE_VAR': value_var, '_VALUE': value})
    
    img_func = {L.SetAdd: make_imgadd,
                L.SetRemove: make_imgremove}[op.__class__]
    img_code = img_func(fresh_vars, auxmap.map, key_var, value_var)
    
    func_name = auxmap.get_maint_func_name(op)
    
    func = L.Parser.ps('''
        def _FUNC(_elem):
            _DECOMP
            _IMGCODE
        ''', subst={'_FUNC': func_name,
                    '<c>_DECOMP': decomp_code,
                    '<c>_IMGCODE': img_code})
    
    return func


class AuxmapFinder(L.NodeVisitor):
    
    """Finds all auxiliary map invariants needed for image-set
    expressions in the program.
    """
    
    def process(self, tree):
        self.uses = OrderedSet()
        
        super().process(tree)
        
        auxmaps = []
        for rel, mask in self.uses:
            map = N.get_auxmap_name(rel, mask)
            auxmap = AuxmapInvariant(map, rel, mask)
            auxmaps.append(auxmap)
        
        return auxmaps
    
    def visit_ImgLookup(self, node):
        self.uses.add((node.rel, node.mask))


class AuxmapTransformer(L.NodeTransformer):
    
    """Insert auxmap maintenance functions, insert calls to maintenance
    functions around SetAdd and SetRemove updates, and replace image-set
    expressions with uses of auxmaps.
    """
    
    def __init__(self, fresh_vars, auxmaps):
        super().__init__()
        self.fresh_vars = fresh_vars
        # Index over auxmaps for fast retrieval.
        self.auxmaps_by_rel = OrderedDict()
        self.auxmaps_by_relmask = OrderedDict()
        for auxmap in auxmaps:
            self.auxmaps_by_rel.setdefault(auxmap.rel, []).append(auxmap)
            self.auxmaps_by_relmask[(auxmap.rel, auxmap.mask)] = auxmap
    
    def visit_Module(self, node):
        node = self.generic_visit(node)
        
        funcs = []
        for rel, auxmaps in self.auxmaps_by_rel.items():
            for auxmap in auxmaps:
                for op in [L.SetAdd(), L.SetRemove()]:
                    func = make_auxmap_maint_func(self.fresh_vars, auxmap, op)
                    funcs.append(func)
        
        node = node._replace(decls=tuple(funcs) + node.decls)
        return node
    
    def visit_RelUpdate(self, node):
        if not isinstance(node.op, (L.SetAdd, L.SetRemove)):
            return node
        
        auxmaps = self.auxmaps_by_rel.get(node.rel, set())
        code = (node,)
        for auxmap in auxmaps:
            func_name = auxmap.get_maint_func_name(node.op)
            call_code = (L.Expr(L.Call(func_name, [L.Name(node.elem)])),)
            code = L.insert_rel_maint(code, call_code, node.op)
        return code
    
    def visit_ImgLookup(self, node):
        auxmap = self.auxmaps_by_relmask.get((node.rel, node.mask), None)
        if auxmap is None:
            return node
        
        key = L.tuplify(node.bounds)
        return L.Parser.pe('_MAP.get(_KEY, Set())',
                           subst={'_MAP': auxmap.map,
                                  '_KEY': key})


def make_auxmap_type(mask, reltype):
    """Given a mask and a relation type, determine the corresponding
    auxiliary map type.
    
    We obtain by lattice join the smallest relation type that is at
    least as big as the given relation type and that has the correct
    arity. This should have the form {(T1, ..., Tn)}. The map type is
    then from a tuple of some Ts to a set of tuples of the remaining Ts.
    
    If no such type exists, e.g. if the given relation type is {Top}
    or a set of tuples of incorrect arity, we instead give the map type
    {Top: Top}.
    """
    arity = len(mask.m)
    bottom_reltype = T.Set(T.Tuple([T.Bottom] * arity))
    top_reltype = T.Set(T.Tuple([T.Top] * arity))
    
    norm_type = reltype.join(bottom_reltype)
    well_typed = norm_type.issmaller(top_reltype)
    
    if well_typed:
        assert (isinstance(norm_type, T.Set) and
                isinstance(norm_type.elt, T.Tuple) and
                len(norm_type.elt.elts) == arity)
        t_bs, t_us = L.split_by_mask(mask, norm_type.elt.elts)
        map_type = T.Map(T.Tuple(t_bs), T.Set(T.Tuple(t_us)))
    else:
        map_type = T.Map(T.Top, T.Top)
    
    return map_type


def define_map(auxmap, symtab):
    """Add a map definition to the symbol table."""
    # Obtain relation symbol.
    relsym = symtab.get_relations().get(auxmap.rel, None)
    if relsym is None:
        raise L.TransformationError('No relation "{}" matching map "{}"'
                                    .format(auxmap.rel, auxmap.map))
    map_type = make_auxmap_type(auxmap.mask, relsym.type)
    symtab.define_map(auxmap.map, type=map_type)
