"""Auxiliary map transformation."""


__all__ = [
    'AuxmapInvariant',
    'AuxmapFinder',
    'AuxmapTransformer',
]


from collections import OrderedDict
from simplestruct import Struct, TypedField

from incoq.util.collections import OrderedSet
from incoq.util.type import typechecked
from incoq.mars.incast import L
from incoq.mars.symtab import N


def insert_rel_maint(update_code, maint_code, op):
    """Insert maintenance code around update code. The maintenance
    goes afterwards for additions and before for removals.
    """
    if isinstance(op, L.SetAdd):
        return update_code + maint_code
    elif isinstance(op, L.SetRemove):
        return maint_code + update_code
    else:
        assert()


class AuxmapInvariant(Struct):
    
    """Auxiliary map invariant."""
    
    map = TypedField(str)
    """Name of variable holding the map."""
    rel = TypedField(str)
    """Name of relation being indexed."""
    mask = TypedField(L.mask)
    """Mask for the indexing."""
    
    def get_maint_func_name(self, op):
        if isinstance(op, L.SetAdd):
            op_name = 'add'
        elif isinstance(op, L.SetRemove):
            op_name = 'remove'
        else:
            assert()
        return N.get_maint_func_name(self.map, self.rel, op_name)


@typechecked
def make_imgadd(target: str, key: L.expr, elem: L.expr):
    """Make code to add elem to the image set for key in target."""
    return L.Parser.pc('''
        if _KEY not in _TARGET:
            _TARGET.mapassign(_KEY, set())
        _TARGET.maplookup(_KEY).add(_ELEM)
        ''', subst={'_TARGET': target,
                    '_KEY': key,
                    '_ELEM': elem})


@typechecked
def make_imgremove(target: str, key: L.expr, elem: L.expr):
    """Make code to remove elem from the image set for key in target."""
    return L.Parser.pc('''
        _TARGET.maplookup(_KEY).remove(_ELEM)
        if len(_TARGET.maplookup(_KEY)) == 0:
            _TARGET.mapdelete(_KEY)
        ''', subst={'_TARGET': target,
                    '_KEY': key,
                    '_ELEM': elem})


@typechecked
def make_auxmap_maint_func(auxmap: AuxmapInvariant, op: L.setupop):
    """Make maintenance function for auxiliary map."""
    # Fresh variables for components of the element.
    vars = N.get_subnames('_elem', len(auxmap.mask.m))
    
    decomp_code = L.DecompAssign(vars, L.Name('_elem'))
    
    key, value = L.split_by_mask(auxmap.mask, vars)
    key = L.tuplify(key)
    value = L.tuplify(value)
    
    if isinstance(op, L.SetAdd):
        img_code = make_imgadd(auxmap.map, key, value)
    elif isinstance(op, L.SetRemove):
        img_code = make_imgremove(auxmap.map, key, value)
    else:
        assert()
    
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
    
    def visit_Imgset(self, node):
        self.uses.add((node.rel, node.mask))


class AuxmapTransformer(L.NodeTransformer):
    """Insert auxmap maintenance functions, insert calls to maintenance
    functions around updates, and replace image-set expressions with
    uses of auxmaps.
    """
    
    def __init__(self, auxmaps):
        super().__init__()
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
                    func = make_auxmap_maint_func(auxmap, op)
                    funcs.append(func)
        
        node = node._replace(decls=tuple(funcs) + node.decls)
        return node
    
    def visit_RelUpdate(self, node):
        auxmaps = self.auxmaps_by_rel.get(node.rel, set())
        code = (node,)
        for auxmap in auxmaps:
            func_name = auxmap.get_maint_func_name(node.op)
            call_code = (L.Expr(L.Call(func_name, [node.value])),)
            code = insert_rel_maint(code, call_code, node.op)
        return code
    
    def visit_Imgset(self, node):
        auxmap = self.auxmaps_by_relmask.get((node.rel, node.mask), None)
        if auxmap is None:
            return node
        
        key = L.tuplify(node.bounds)
        return L.Parser.pe('_MAP.mapget(_KEY, set())',
                           subst={'_MAP': auxmap.map,
                                  '_KEY': key})
