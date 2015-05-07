"""Object-domain / pair-domain translation."""


__all__ = [
    'to_pairdomain',
    'to_objdomain',
]


from incoq.util.collections import OrderedSet
import incoq.compiler.incast as L

from .pairrel import (make_mrel, is_mrel, make_frel, is_frel,
                      get_frel_field, make_maprel, is_maprel,
                      is_specialrel)
from .objcomp import flatten_comp, unflatten_comp


class UpdateToPairTransformer(L.NodeTransformer):
    
    """Convert updates to the relational domain."""
    
    def __init__(self, use_mset, fields, use_mapset, input_rels):
        super().__init__()
        self.use_mset = use_mset
        self.fields = OrderedSet(fields)
        self.use_mapset = use_mapset
        self.input_rels = input_rels
    
    def visit_Module(self, node):
        node = self.generic_visit(node)
        
        decls = ()
        if self.use_mset:
            decls += L.pc('''
                M = MSet()
                ''', subst={'M': L.sn(make_mrel())})
        for field in self.fields:
            decls += L.pc('''
                F = FSet()
                ''', subst={'F': L.sn(make_frel(field))})
        if self.use_mapset:
            decls += L.pc('''
                MAP = MAPSet()
                ''', subst={'MAP': L.sn(make_maprel())})
        
        node = node._replace(body=decls + node.body)
        return node
    
    def visit_Assign(self, node):
        node = self.generic_visit(node)
        
        if L.is_attrassign(node):
            cont, field, value = L.get_attrassign(node)
            if field not in self.fields:
                return node
            return L.pc('''
                FSET.add((CONT, VALUE))
                ''', subst={'FSET': L.ln(make_frel(field)),
                            'CONT': cont,
                            'VALUE': value})
        
        else:
            return node
    
    def visit_Delete(self, node):
        node = self.generic_visit(node)
        
        if L.is_delattr(node):
            cont, field = L.get_delattr(node)
            if field not in self.fields:
                return node
            return L.pc('''
                FSET.remove((CONT, CONT.FIELD))
                ''', subst={'FSET': L.ln(make_frel(field)),
                            'CONT': cont,
                            '@FIELD': field})
        
        else:
            return node
    
    def visit_SetUpdate(self, node):
        node = self.generic_visit(node)
        
        if not self.use_mset:
            return node
        
        # Ignore updates to input relations.
        if (isinstance(node.target, L.Name) and
            node.target.id in self.input_rels):
            return node
        
        code = L.pc('''
            M.OP((CONT, ELEM))
            ''', subst={'M': L.ln(make_mrel()),
                        '@OP': node.op,
                        'CONT': node.target,
                        'ELEM': node.elem})
        return code
    
    def visit_AssignKey(self, node):
        node = self.generic_visit(node)
        
        if not self.use_mapset:
            return node
        
        code = L.pc('''
            MAPSET.add((TARGET, KEY, VALUE))
            ''', subst={'MAPSET': L.ln(make_maprel()),
                        'TARGET': node.target,
                        'KEY': node.key,
                        'VALUE': node.value})
        return code
    
    def visit_DelKey(self, node):
        node = self.generic_visit(node)
        
        if not self.use_mapset:
            return node
        
        code = L.pc('''
            MAPSET.remove((TARGET, KEY, TARGET[KEY]))
            ''', subst={'MAPSET': L.ln(make_maprel()),
                        'TARGET': node.target,
                        'KEY': node.key})
        return code


class UpdateToObjTransformer(L.NodeTransformer):
    
    """Convert updates to the object domain."""
    
    def __init__(self, namegen):
        super().__init__()
        self.namegen = namegen
    
    def visit_Assign(self, node):
        # Get rid of pair relation declarations.
        
        node = self.generic_visit(node)
        
        if L.is_varassign(node):
            name, _value = L.get_varassign(node)
            if is_specialrel(name):
                return ()
        
        return node
    
    def visit_SetUpdate(self, node):
        node = self.generic_visit(node)
        
        if not node.is_varupdate():
            return node
        rel = node.target.id
        elem = node.elem
        
        if not is_specialrel(rel):
            return node
        
        code = ()
        
        # Insert decomposition of element if it's not
        # an AST of a tuple of the right arity.
        if is_mrel(rel) or is_frel(rel):
            if isinstance(elem, L.Tuple) and len(elem.elts) == 2:
                cont, item = elem.elts
            else:
                prefix = self.namegen.next_prefix()
                cont = prefix + 'cont'
                item = prefix + 'item'
                code += L.pc('''
                    CONT, ITEM = ELEM
                    ''', subst={'CONT': cont,
                                'ITEM': item,
                                'ELEM': elem})
        elif is_maprel(rel):
            if isinstance(elem, L.Tuple) and len(elem.elts) == 3:
                map, key, value = elem.elts
            else:
                prefix = self.namegen.next_prefix()
                map = prefix + 'map'
                key = prefix + 'key'
                value = prefix + 'value'
                code = L.pc('''
                    MAP, KEY, VALUE = ELEM
                    ''', subst={'MAP': map,
                                'KEY': key,
                                'VALUE': value,
                                'ELEM': elem})
        
        if is_mrel(rel):
            code += L.pc('''
                CONT.OP(ITEM)
                ''', subst={'CONT': cont,
                            '@OP': node.op,
                            'ITEM': item})
        elif is_frel(rel):
            field = get_frel_field(rel)
            if node.op == 'add':
                code += L.pc('''
                    CONT.FIELD = ITEM
                    ''', subst={'CONT': cont,
                                '@FIELD': field,
                                'ITEM': item})
            elif node.op == 'remove':
                code += L.pc('''
                    del CONT.FIELD
                    ''', subst={'CONT': cont,
                                '@FIELD': field})
            else:
                assert()
        
        elif is_maprel(rel):
            if node.op == 'add':
                code += L.pc('''
                    MAP[KEY] = VALUE
                    ''', subst={'MAP': map,
                                'KEY': key,
                                'VALUE': value})
            elif node.op == 'remove':
                code += L.pc('''
                    del MAP[KEY]
                    ''', subst={'MAP': map,
                                'KEY': key})
            else:
                assert()
        
        else:
            assert()
        
        return code


def flatten_all_comps(tree, input_rels):
    """Flatten all object comprehensions in the program, and return
    a tuple of the new tree, a boolean for whether the M-set was
    used, an OrderedSet of all fields replaced, and a boolean for
    whether the MAP set was used.
    """
    class Flattener(L.QueryMapper):
        def process(self, tree):
            self.use_mset = False
            self.fields = OrderedSet()
            self.use_mapset = False
            tree = super().process(tree)
            return tree, self.use_mset, self.fields, self.use_mapset
        
        def map_Comp(self, node):
            new_comp, new_mset, new_fields, new_mapset = \
                flatten_comp(node, input_rels)
            self.use_mset |= new_mset
            self.fields.update(new_fields)
            self.use_mapset |= new_mapset
            return new_comp
    
    return Flattener.run(tree)

def unflatten_all_comps(tree):
    """Unflatten all object comprehensions in the program, and return
    the new tree.
    """
    class Unflattener(L.QueryMapper):
        def map_Comp(self, node):
            return unflatten_comp(node)
    
    return Unflattener.run(tree)


def is_retrievalchain(node):
    """Return whether the given node is a chain of retrievals
    such as a[b.c].d. Trivially, a single Name is a chain.
    """
    if isinstance(node, L.Name):
        return True
    elif isinstance(node, L.Attribute):
        return is_retrievalchain(node.value)
    elif isinstance(node, L.Subscript):
        if not isinstance(node.slice, L.Index):
            return False
        return (is_retrievalchain(node.value) and
                is_retrievalchain(node.slice.value))
    else:
        return False

def get_retrieval_params(node):
    """Return a tuple of parameters in a retrieval chain, e.g.
    ('a', 'b') for a[b.c].d.
    """
    assert is_retrievalchain(node)
    
    params = ()
    class Vis(L.NodeVisitor):
        def visit_Name(self, node):
            nonlocal params
            params += (node.id,)
    Vis.run(node)
    
    return params


class AggregatePreprocessor(L.NodeTransformer):
    
    """Expand aggregates of variables or retrievals into
    aggregates of object-domain comprehensions.
    """
    
    def visit_Aggregate(self, node):
        node = self.generic_visit(node)
        
        operand = node.value
        if isinstance(operand, L.Comp):
            return node
        if not is_retrievalchain(operand):
            # Bailout, looks like we won't be able to incrementalize
            # this later anyway.
            return node
        
        # Replace with {_e for _e in OPERAND}.
        # This case is for both single vars and retrieval chains.
        # The comp's options are inherited from the aggregate.
        params = get_retrieval_params(operand)
        elem = '_e'
        clause = L.Enumerator(target=L.sn(elem),
                              iter=operand)
        node = node._replace(value=L.Comp(resexp=L.ln(elem),
                                          clauses=(clause,),
                                          params=params,
                                          options=node.options))
        return node


def to_pairdomain(tree, manager, input_rels):
    """Convert a program to the pair domain, rewriting updates and
    queries.
    """
    tree = AggregatePreprocessor.run(tree)
    tree, use_mset, fields, use_mapset = flatten_all_comps(tree, input_rels)
    tree = UpdateToPairTransformer.run(tree, use_mset, fields, use_mapset,
                                       input_rels)
    manager.use_mset = use_mset
    manager.fields = list(fields)
    manager.use_mapset = use_mapset
    return tree

def to_objdomain(tree, manager):
    """Convert a program to the object domain, rewriting updates and
    queries.
    """
    tree = UpdateToObjTransformer.run(tree, manager.namegen)
    tree = unflatten_all_comps(tree)
    return tree
