"""Membership and condition clauses, which are the components of joins."""

### TODO: Optimize subtract()/augment() to cancel out subclause/augclause


__all__ = [
    'apply_subst_tuple',
    'inst_wildcards',
    'vars_from_tuple',
    
    'Clause',
    
    'EnumClause',
    'SubClause',
    'AugClause',
    'LookupClause',
    'SingletonClause',
    'DeltaClause',
    'CondClause',
    
    'ClauseFactory',
]


from abc import ABCMeta, abstractmethod, abstractclassmethod

from simplestruct import Struct, MetaStruct, TypedField
from iast.python.python34 import ContextSetter

from oinc.util.type import checktype
from oinc.util.seq import elim_duplicates
import oinc.compiler.incast as L
from oinc.compiler.set import (Mask, AuxmapSpec, make_bindmatch,
                               make_tuplematch)

from .order import Rate


class ABCMetaStruct(MetaStruct, ABCMeta):
    pass

class ABCStruct(Struct, metaclass=ABCMetaStruct):
    pass


def apply_subst_tuple(vars, subst):
    """Given a tuple of variables, return the result of applying a
    substitution. The substitution keys are input var names, and the
    values are either output var names, or else callables that take
    in an input var name and produce an output var name.
    """
    new_vars = []
    for v in vars:
        newval = subst.get(v, v)
        if not isinstance(newval, str):
            newval = newval(v)
        new_vars.append(newval)
    return tuple(new_vars)

def inst_wildcards(vars):
    """Given a tuple of variables and wildcards, return a tuple where
    wildcards are replaced with successive fresh vars _v1, ... _vn.
    """
    namer = L.NameGenerator('_v{}', 1)
    vars = apply_subst_tuple(vars, {'_': lambda v: namer.next()})
    return vars

def vars_from_tuple(vars):
    """Given a tuple of variables, return a tuple with duplicates
    and wilcards removed.
    """
    return elim_duplicates(tuple(v for v in vars if v != '_'))


class Clause(metaclass=ABCMeta):
    
    """Abstract base class for (unordered) join clauses."""
    
    class ClauseKind:
        """Enumeration class for KIND constants."""
    KIND_ENUM = ClauseKind()
    KIND_COND = ClauseKind()
    
    kind = None
    
    isdelta = False
    """True for clauses that represent the enumerator affected by
    an update.
    """
    
    enumlhs = ()
    """For enumerators, a tuple of the terms on the left-hand-side,
    in order, including duplicates and wildcards. For conditions,
    the empty tuple.
    """
    
    enumrel = None
    """Name of the iterated relation. None for conditions and for
    enumerators that are not over (expressions derived from) set
    variables.
    """
    
    vars = ()
    """For enumerators, same as enumvars. For conditions, a tuple
    of the variables the condition depends on.
    """
    
    eqvars = None
    """For a condition that equates variables, a pair of the
    equated variables. None for other conditions and for
    enumerators.
    """
    
    robust = True
    """True if this enumerator's meaning is independent of context
    (i.e., relies only on relations, which are global).
    """
    
    inc_safe = True
    """True if, provided that this clause is robust, it would be safe
    to incrementalize a comprehension having this clause.
    """
    
    demname = None
    demparams = ()
    """For an enumerator whose RHS is demand-driven, the corresponding
    query name and demand parameters.
    """
    
    @property
    def has_demand(self):
        return self.demname is not None
    
    @property
    def enumvars(self):
        """For enumerators, a tuple of the enumeration variables in
        the order they occur, omitting duplicates and wildcards. For
        conditions, the empty tuple.
        """
        return vars_from_tuple(self.enumlhs)
    
    @property
    def has_wildcards(self):
        """For an enumerator, True iff there are any wildcards on
        the LHS. For a condition, False.
        """
        return any(v == '_' for v in self.enumlhs)
    
    # The following attributes are enumlhs masks -- tuples of bools
    # whose positions correspond to entries in enumlhs. For conditions
    # these are just the empty tuple, since enumlhs is the empty
    # tuple.
    
    @property
    def pat_mask(self):
        """Enumlhs mask. True means the position is subject to
        pattern matching. Vars at that position can be renamed.
        """
        return tuple(True for _ in self.enumlhs)
    
    @property
    def con_mask(self):
        """Enumlhs mask. True means the position is constrained by
        the enumerator. Vars are considered unconstrained if they
        only appear at unconstrained positions.
        """
        return tuple(True for _ in self.enumlhs)
    
    @property
    def tagsin_mask(self):
        """Enumlhs mask. True means this clause can be filtered by
        a tag over the var at that position.
        """
        return tuple(True for _ in self.enumlhs)
    
    @property
    def tagsout_mask(self):
        """Enumlhs mask. True means this clause can introduce a tag
        over a var at that position.
        """
        return tuple(True for _ in self.enumlhs)
    
    # For the above masks, these properties return the vars in
    # enumvars that appear in a position in enumlhs that satisfies
    # the mask.
    
    @property
    def enumvars_tagsin(self):
        return vars_from_tuple(
            v for v, b in zip(self.enumlhs, self.tagsin_mask) if b)
    
    @property
    def enumvars_tagsout(self):
        return vars_from_tuple(
            v for v, b in zip(self.enumlhs, self.tagsout_mask) if b)
    
    def get_domain_constrs(self, prefix):
        """For an enumerator with non-None enumrel, return a sequence
        of domain constraints. For all other clauses return an empty
        sequence. Names of enumeration variables in the constraints
        get the supplied prefix.
        """
        if self.enumrel is None:
            return ()
        dom = self.enumrel
        
        constrs = []
        
        # If there's only one component on the lhs, this is not
        # (necessarily) a set of singleton tuples, so don't emit
        # tuple-based constraints.
        if len(self.enumlhs) == 1:
            var = self.enumlhs[0]
            if var != '_':
                constrs.append((dom, prefix + var))
        
        else:
            subdoms = [dom + '.' + str(i)
                       for i in range(1, len(self.enumlhs) + 1)]
            constr = (dom, tuple(['<T>'] + subdoms))
            constrs.append(constr)
            
            for i, var in enumerate(self.enumlhs, 1):
                if var == '_':
                    continue
                constr = (dom + '.' + str(i), prefix + var)
                constrs.append(constr)
        
        return tuple(constrs)
    
    def get_membership_constrs(self):
        """Return a sequence of labeled edge triples (x, y, i) meaning
        that x is constrained to be the ith component of a tuple in y.
        If i is None then x itself is an element of y. If enumrel is
        None return an empty sequence.
        """
        if self.enumrel is None:
            return ()
        dom = self.enumrel
        
        edges = []
        
        if len(self.enumlhs) == 1:
            var = self.enumlhs[0]
            if var != '_':
                edges.append((var, dom, None))
        
        else:
            for i, var in enumerate(self.enumlhs, 1):
                if var == '_':
                    continue
                edges.append((var, dom, i))
        
        return tuple(edges)
    
    @abstractclassmethod
    def from_AST(self, node, factory):
        """Construct an instance of this clause from an AST.
        For an enumerator, this should be an Enumerator node of
        a certain form, depending on the subclass. For a condition,
        this is an expression node. Raise TypeError if construction
        from the given AST is not appropriate.
        
        factory is a ClauseFactory (instance or class) that may be
        used to construct other clauses that are needed to construct
        this one.
        """
    
    @abstractmethod
    def to_AST(self):
        """Return an AST representing this clause. For an enumerator,
        this is an Enumerator node. For a condition, this is an
        expression node.
        """
    
    def __str__(self):
        clast = self.to_AST()
        s = L.ts(clast).strip()
        if isinstance(clast, L.Enumerator):
            # Get rid of "for" at the beginning.
            s = s[s.find(' ') + 1:]
        return s
    
    # User code should call ClauseFactory methods rather than these
    # helpers directly.
    
    def rewrite_subst(self, subst, factory):
        """See ClauseFactory."""
        clast = self.to_AST()
        if self.kind is Clause.KIND_ENUM:
            lhs = clast.target
            lhs = L.VarRenamer.run(lhs, subst)
            clast = clast._replace(target=lhs)
        else:
            clast = L.VarRenamer.run(clast, subst)
        return factory.from_AST(clast)
    
    def rewrite_lhs(self, subst, factory):
        """See ClauseFactory."""
        if self.kind is not Clause.KIND_ENUM:
            return self
        clast = self.to_AST()
        lhs = clast.target
        lhs = L.VarRenamer.run(lhs, subst)
        clast = clast._replace(target=lhs)
        return factory.from_AST(clast)
    
    def rewrite_rel(self, rel, factory):
        """See ClauseFactory."""
        raise TypeError
    
    def subtract_inner(self, excl, factory):
        """See ClauseFactory."""
        # Default implementation is to use subtract.
        # Must override if this clause is a wrapper
        # around another clause.
        return factory.subtract(self, excl)
    
    def fits_string(self, bindenv, s):
        """Return True if s is an informal characterization of this
        clause (under binding environment bindenv) that a user may
        write to refer to it. Useful for letting the user specify
        clause priority overrides.
        """
        return False
    
    def needs_filtering(self, bindenv):
        """For enumerators, return whether or not a demand-filtered
        version of this clause should be used. For conditions raise
        TypeError.
        """
        if self.kind is not Clause.KIND_ENUM:
            raise TypeError
        # By default, use a filter if any tagsin position is not
        # bound.
        return not set(self.enumvars_tagsin).issubset(bindenv)
    
    @abstractmethod
    def rate(self, bindenv):
        """For the join heuristic, return a numerical ranking for this
        clause under a binding environment. A binding environment is
        a sequence of names of variables that are considered bound.
        See oinc.comp.order.
        """
    
    def get_determined_vars(self, bindenv):
        """Return a tuple of enumvars that are functionally determined
        by the union of the given bound vars and the remaining vars in
        this clause that aren't returned. The returned tuple may have
        duplicates and may include the given vars.
        """
        return ()
    
    @abstractmethod
    def get_code(self, bindenv, body):
        """Return code to run this clause in the way implied by a
        binding environment. body is the code that is enclosed in,
        or follows, this clause.
        """


class EnumClause(Clause, ABCStruct):
    
    """An normal enumeration (membership constraint) clause
    over a relation.
    """
    
    kind = Clause.KIND_ENUM
    
    lhs = TypedField(str, seq=True)
    """Tuple of variables on left-hand side."""
    rel = TypedField(str)
    """Name of iterated relation."""
    
    @classmethod
    def from_expr(cls, node):
        """Construct from a membership condition expression of form
        
            <vars> in <rel>
        
        Note that this is syntactically different from the form used
        in comprehensions, even though their textual representation
        in source code is the same.
        """
        checktype(node, L.AST)
        
        left, op, right = L.get_cmp(node)
        checktype(op, L.In)
        lhs = L.get_vartuple(left)
        rel = L.get_name(right)
        return cls(lhs, rel)
    
    @classmethod
    def from_AST(cls, node, factory):
        """Construct from an Enumerator node of form
        
            <vars> in <rel>
        
        Alternatively, the rhs may be a setmatch of a rel, where
        the mask is a lookupmask and the key is a vartuple.
        """
        checktype(node, L.Enumerator)
        
        lhs = L.get_vartuple(node.target)
        rhs = node.iter
        
        if L.is_name(rhs):
            rel = L.get_name(rhs)
        
        elif isinstance(rhs, L.SetMatch) and L.is_vartuple(rhs.key):
            keyvars = L.get_vartuple(rhs.key)
            # Make sure we're dealing with a lookupmask and that the
            # key vars agree with the mask.
            mask = Mask(rhs.mask)
            assert mask.is_lookupmask
            assert mask.lookup_arity == len(keyvars)
            
            lhs = keyvars + lhs
            rel = L.get_name(rhs.target)
        
        else:
            raise TypeError
        
        return cls(lhs, rel)
    
    def __init__(self, lhs, rel):
        self.enumlhs = self.lhs
        self.enumrel = self.rel
        self.vars = self.enumvars
    
    def to_AST(self):
        return L.Enumerator(L.tuplify(self.lhs, lval=True),
                            L.ln(self.rel))
    
    def rewrite_rel(self, rel, factory):
        # We specifically construct an EnumClause (not an instance of
        # a subclass) and rely on the factory to turn that into an
        # appropriate clause. This is to play nice with the object
        # clauses in oinc/obj/objclause.py.
        cl = EnumClause(self.enumlhs, rel)
        clast = cl.to_AST()
        return factory.from_AST(clast)
    
    def fits_string(self, bindenv, s):
        mask = Mask.from_vars(self.lhs, bindenv)
        return s == AuxmapSpec(self.rel, mask).lookup_name
    
    def rate(self, bindenv):
        mask = Mask.from_vars(self.lhs, bindenv)
        if mask.is_allbound:
            return Rate.CONSTANT_MEMBERSHIP
        elif mask.is_allunbound:
            return Rate.NOTPREFERRED
        else:
            return Rate.NORMAL
    
    def get_code(self, bindenv, body):
        mask = Mask.from_vars(self.lhs, bindenv)
        bvars, uvars, _eqs = mask.split_vars(self.lhs)
        return make_bindmatch(self.rel, mask, bvars, uvars, body)


class SubClause(Clause, ABCStruct):
    
    """An enumerator that skips over a specified element."""
    
    kind = Clause.KIND_ENUM
    
    robust = False
    
    cl = TypedField(Clause)
    """Underlying clause."""
    excl = TypedField(L.expr)
    """Expression whose value is to be excluded."""
    
    pat_mask = None
    con_mask = None
    tagsin_mask = None
    tagsout_mask = None
    
    @classmethod
    def from_AST(cls, node, factory):
        """Construct from Enumerator node of form
        
            <vars> in <rel> - {<expr>}
        """
        checktype(node, L.Enumerator)
        
        rhs, excl = L.get_singsub(node.iter)
        
        innernode = node._replace(iter=rhs)
        innerclause = factory.from_AST(innernode)
        
        return cls(innerclause, excl)
    
    def __init__(self, cl, excl):
        for attr in [
            'isdelta', 'enumlhs', 'enumrel',
            'pat_mask', 'con_mask', 'tagsin_mask', 'tagsout_mask',
            'vars', 'eqvars', 'demname', 'demparams']:
            setattr(self, attr, getattr(cl, attr))
    
    def to_AST(self):
        code = self.cl.to_AST()
        assert isinstance(code, L.Enumerator)
        code = code._replace(iter=L.pe('ITER - {EXCL}',
                                       subst={'ITER': code.iter,
                                              'EXCL': self.excl}))
        return code
    
    def rewrite_rel(self, rel, factory):
        new_cl = self.cl.rewrite_rel(rel, factory)
        return self._replace(cl=new_cl)
    
    def subtract_inner(self, excl, factory):
        new_cl = self.cl.subtract_inner(excl, factory)
        return self._replace(cl=new_cl)
    
    def fits_string(self, mask, s):
        return self.cl.fits_string(mask, s)
    
    def rate(self, bindenv):
        return self.cl.rate(bindenv)
    
    def get_code(self, bindenv, body):
        guard_code = L.pc('''
            if LHS != EXCL:
                BODY
            ''', subst={'LHS': L.tuplify(self.cl.enumlhs),
                        'EXCL': self.excl,
                        '<c>BODY': body})
        
        return self.cl.get_code(bindenv, guard_code)


class AugClause(Clause, ABCStruct):
    
    """An enumerator that runs for one extra element."""
    
    kind = Clause.KIND_ENUM
    
    robust = False
    
    cl = TypedField(Clause)
    """Underlying clause."""
    extra = TypedField(L.expr)
    """Expression whose value is to be added."""
    
    pat_mask = None
    con_mask = None
    tagsin_mask = None
    tagsout_mask = None
    
    @classmethod
    def from_AST(cls, node, factory):
        """Construct from Enumerator node of form
        
            <vars> in <rel> + {<expr>}
        """
        checktype(node, L.Enumerator)
        
        rhs, extra = L.get_singadd(node.iter)
        
        innernode = node._replace(iter=rhs)
        innerclause = factory.from_AST(innernode)
        
        return cls(innerclause, extra)
    
    def __init__(self, cl, extra):
        for attr in [
            'isdelta', 'enumlhs', 'enumrel',
            'pat_mask', 'con_mask', 'tagsin_mask', 'tagsout_mask',
            'vars', 'eqvars', 'demname', 'demparams']:
            setattr(self, attr, getattr(cl, attr))
    
    def to_AST(self):
        code = self.cl.to_AST()
        assert isinstance(code, L.Enumerator)
        code = code._replace(iter=L.pe('ITER + {EXTRA}',
                                       subst={'ITER': code.iter,
                                              'EXTRA': self.extra}))
        return code
    
    def rewrite_rel(self, rel, factory):
        new_cl = self.cl.rewrite_rel(rel, factory)
        return self._replace(cl=new_cl)
    
    def subtract_inner(self, excl, factory):
        new_cl = self.cl.subtract_inner(excl, factory)
        return self._replace(cl=new_cl)
    
    def fits_string(self, mask, s):
        return self.cl.fits_string(mask, s)
    
    def rate(self, bindenv):
        return self.cl.rate(bindenv)
    
    def get_code(self, bindenv, body):
        # Hackish: Rather than add a factory parameter to this method,
        # I'm just going to forego the use of ClauseFactory.bind() and
        # construct SingletonClause directly.
        boundcl = SingletonClause(self.enumlhs, self.extra)
        code = self.cl.get_code(bindenv, body)
        code += boundcl.get_code(bindenv, body)
        return code


class LookupClause(EnumClause, ABCStruct):
    
    """An enumerator over a singleton set of an SMLookup node.
    Basically acts like a normal EnumClause, but the forward
    direction takes constant time due to the functional
    dependency from keys to value.
    """
    
    lhs = TypedField(str, seq=True)
    """Enumeration variables."""
    rel = TypedField(str)
    """Name of iterated relation."""
    
    @classmethod
    def from_AST(cls, node, factory):
        """Construct from an Enumerator node of form
        
            var in {<rel>.smlookup(<mask>, <key vars>)}
        
        """
        checktype(node, L.Enumerator)
        
        var = L.get_name(node.target)
        sm = L.get_singletonset(node.iter)
        checktype(sm, L.SMLookup)
        rel = L.get_name(sm.target)
        mask = Mask(sm.mask)
        keyvars = L.get_vartuple(sm.key)
        # Ensure the mask is consistent with how it's used.
        if mask != Mask.from_keylen(len(keyvars)):
            raise TypeError
        
        lhs = keyvars + (var,)
        return cls(lhs, rel)
    
    def to_AST(self):
        mask = Mask.from_keylen(len(self.lhs) - 1)
        keyvars = self.lhs[:-1]
        var = self.lhs[-1]
        sm = L.SMLookup(L.ln(self.rel), mask.make_node().s,
                        L.tuplify(keyvars), None)
        return L.Enumerator(L.sn(var), L.Set((sm,)))
    
    def rewrite_subst(self, subst, factory):
        # The normal rewriting won't get the smlookup keys.
        new_lhs = apply_subst_tuple(self.lhs, subst)
        return self._replace(lhs=new_lhs)
    
    def rate(self, bindenv):
        mask = Mask.from_vars(self.lhs, bindenv)
        if mask.is_keymask:
            return Rate.CONSTANT
        return super().rate(bindenv)


class SingletonClause(Clause, ABCStruct):
    
    """An enumerator over a singleton set, i.e., that binds its
    left-hand side to a single value.
    """
    
    kind = Clause.KIND_ENUM
    
    robust = False
    
    lhs = TypedField(str, seq=True)
    """Enumeration variables."""
    val = TypedField(L.expr)
    """Expression computing value of singleton element."""
    
    @classmethod
    def from_expr(cls, node):
        """Construct from a condition expression of form
        
            <vars> == <rel>
        """
        checktype(node, L.AST)
        
        left, op, val = L.get_cmp(node)
        checktype(op, L.Eq)
        lhs = L.get_vartuple(left)
        
        return cls(lhs, val)
    
    @classmethod
    def from_AST(cls, node, factory):
        """Construct from Enumerator node of form
        
            <vars> in {<expr>}
        """
        checktype(node, L.Enumerator)
        
        lhs = L.get_vartuple(node.target)
        val = L.get_singletonset(node.iter)
        
        return cls(lhs, val)
    
    def __init__(self, lhs, val):
        self.enumlhs = self.lhs
        self.enumrel = None
        self.vars = self.enumvars
    
    def to_AST(self):
        return L.Enumerator(L.tuplify(self.lhs, lval=True),
                            L.Set((self.val,)))
    
    def rate(self, bindenv):
        return Rate.CONSTANT
    
    def get_code(self, bindenv, body):
        mask = Mask.from_vars(self.lhs, bindenv)
        bvars, uvars, _eqs = mask.split_vars(self.lhs)
        return make_tuplematch(self.val, mask, bvars, uvars, body)


class DeltaClause(Clause, ABCStruct):
    
    """Clause for the update to a join."""
    
    kind = Clause.KIND_ENUM
    
    isdelta = True
    robust = False
    
    lhs = TypedField(str, seq=True)
    """Enumeration variables."""
    rel = TypedField(str)
    """Relation that was updated."""
    val = TypedField(L.expr)
    """Expression computing value of singleton element."""
    limit = TypedField(int)
    
    @classmethod
    def from_AST(cls, node, factory):
        """Construct from Enumerator node of form
        
            <vars> in deltamatch(<rel>, <mask>, <val>, <limit>)
        """
        checktype(node, L.Enumerator)
        
        lhs = L.get_vartuple(node.target)
        checktype(node.iter, L.DeltaMatch)
        rel = L.get_name(node.iter.target)
        mask = Mask(node.iter.mask)
        val = node.iter.elem
        limit = node.iter.limit
        if limit not in [0, 1]:
            raise TypeError
        
        inferred_mask = Mask.from_vars(lhs, lhs)
        assert mask == inferred_mask
        
        return cls(lhs, rel, val, limit)
    
    def __init__(self, lhs, rel, val, limit):
        assert limit in [0, 1]
        self.enumlhs = self.lhs
        self.enumrel = rel
        self.vars = self.enumvars
    
    def to_AST(self):
        mask = Mask.from_vars(self.lhs, self.lhs)
        return L.Enumerator(L.tuplify(self.lhs, lval=True),
                            L.DeltaMatch(L.ln(self.rel), mask.make_node().s,
                                         self.val, self.limit))
    
    def rewrite_rel(self, rel, factory):
        # In the case of delta clauses over pair relations,
        # this allows the use of the pair relation to be filtered.
        return self._replace(rel=rel)
    
    def needs_filtering(self, bindenv):
        return False
    
    def rate(self, bindenv):
        return Rate.FIRST
    
    def get_code(self, bindenv, body):
        deltamask = Mask.from_vars(self.lhs, self.lhs)
        mask = Mask.from_vars(self.lhs, bindenv)
        bvars, uvars, _eqs = mask.split_vars(self.lhs)
        if mask.has_wildcards:
            # Can this be streamlined into something more readable,
            # like expressing the deltamatch as an If-guard? 
            val = L.DeltaMatch(L.ln(self.rel), deltamask.make_node().s,
                               self.val, self.limit)
            return L.pc('''
                for UVARS in setmatch(VAL, MASK, BVARS):
                    BODY
                ''', subst={'VAL': val,
                            'MASK': mask.make_node(),
                            'BVARS': L.tuplify(bvars),
                            'UVARS': L.tuplify(uvars, lval=True),
                            '<c>BODY': body})
        else:
            return make_tuplematch(self.val, mask, bvars, uvars, body)


class CondClause(Clause, ABCStruct):
    
    """A condition expression clause."""
    
    kind = Clause.KIND_COND
    
    cond = TypedField(L.expr)
    """Condition expression."""
    
    @classmethod
    def from_AST(cls, node, factory):
        """Construct from expression node."""
        checktype(node, L.expr)
        
        return cls(node)
    
    def __init__(self, cond):
        self.vars = tuple(L.VarsFinder.run(cond, ignore_functions=True))
        
        if L.is_vareqcmp(cond):
            self.eqvars = L.get_vareqcmp(cond)
        else:
            self.eqvars = None
    
    def to_AST(self):
        return self.cond
    
    def fits_string(self, bindenv, s):
        return self.cond == L.pe(s)
    
    def rate(self, bindenv):
        if set(self.vars).issubset(bindenv):
            return Rate.CONSTANT
        else:
            return Rate.UNRUNNABLE
    
    def get_code(self, bindenv, body):
        assert set(self.vars).issubset(bindenv)
        code = L.pc('''
            if COND:
                BODY
            ''', subst={'COND': self.cond, '<c>BODY': body})
        return code


class ClauseFactory:
    
    """Factory for constructing clauses from ASTs.
    Instantiation not needed.
    """
    
    typecheck = True
    """Whether or not to use clauses that insert type checks
    in generated code.
    """
    
    @classmethod
    def get_clause_kinds(cls):
        """Clause classes to use to try to construct a clause from
        an AST. Subclasses should override this to prepend their own
        clause classes to the list.
        """
        return [
            EnumClause,
            SubClause,
            AugClause,
            # Try LookupClause before SingletonClause since
            # the former's more specific.
            LookupClause,
            SingletonClause,
            DeltaClause,
            CondClause,
        ]
    
    @classmethod
    def from_AST(cls, node):
        # Try each clause until one doesn't raise TypeError.
        for enumcls in cls.get_clause_kinds():
            try:
                return enumcls.from_AST(node, cls)
            except TypeError:
                pass
        else:
            raise TypeError('Cannot construct clause from node: ' +
                            L.ts(node))
    
    @classmethod
    def rewrite_subst(cls, cl, subst):
        """Rewrite a clause to substitute variables in conditions
        and on the LHS of enumerators, according to the given mapping.
        The RHS of enumerators is (usually) unaffected. The substitution
        mapping is as for incast.VarRenamer. Also applies to conditions.
        """
        return cl.rewrite_subst(subst, cls)
    
    @classmethod
    def rewrite_lhs(cls, cl, subst):
        """As above but strictly only apply to the LHS of an enumerator."""
        return cl.rewrite_lhs(subst, cls)
    
    @classmethod
    def rewrite_rel(cls, cl, rel):
        """For an enumerator over a relation (i.e. non-None enumrel),
        produce a clause with rel as the new iterated relation.
        For all other clauses, raise TypeError.
        """
        return cl.rewrite_rel(rel, cls)
    
    # Note that subtract/augment should produce the opposite kind
    # of clause for negated enums.
    
    @classmethod
    def bind(cls, cl, val, *, augmented):
        """For an enumerator, produce a clause where the LHS is
        bound directly to val. val need not be a value in the RHS.
        For conditions, raise TypeError.
        """
        limit = 0 if augmented else 1
        return DeltaClause(cl.enumlhs, cl.enumrel, val, limit)
    
    @classmethod
    def subtract(cls, cl, excl):
        """For an enumerator, produce a subtractive clause that
        excludes the given element. For conditions, raise TypeError.
        """
        if cl.kind is not cl.KIND_ENUM:
            raise TypeError
        return SubClause(cl, excl)
    
    @classmethod
    def subtract_inner(cls, cl, excl):
        """As above, but apply the subtraction to the innermost clause,
        so an outer augmented clause can still undo it.
        """
        if cl.kind is not cl.KIND_ENUM:
            raise TypeError
        return cl.subtract_inner(excl, cls)
    
    @classmethod
    def augment(cls, cl, extra):
        """For an enumerator, produce an augmented clause that
        includes the given element. For conditions, raise TypeError.
        """
        if cl.kind is not cl.KIND_ENUM:
            raise TypeError
        return AugClause(cl, extra)
    
    @classmethod
    def membercond_to_enum(cls, cl):
        """For a condition clause that expresses a membership, return
        an equivalent enumerator clause. For other kinds of conditions,
        return the same clause. For enumerators, raise TypeError.
        """
        if cl.kind is not Clause.KIND_COND:
            raise TypeError
        
        compre_ast = None
        clast = cl.to_AST()
        if L.is_cmp(clast):
            lhs, op, rhs = L.get_cmp(clast)
            if (L.is_vartuple(lhs) and
                isinstance(op, L.In)):
                compre_ast = L.Enumerator(
                        L.tuplify(L.get_vartuple(lhs), lval=True),
                        rhs)
        
        if compre_ast is None:
            return cl
        else:
            return cls.from_AST(compre_ast)
    
    @classmethod
    def enum_to_membercond(cls, cl):
        """For enumerators, return an equivalent membership clause.
        For conditions, raise TypeError.
        """
        if cl.kind is not Clause.KIND_ENUM:
            raise TypeError
        
        clast = cl.to_AST()
        lhs = clast.target
        lhs = ContextSetter.run(lhs, L.Load)
        rhs = clast.iter
        cond_ast = L.cmp(lhs, L.In(), rhs)
        return cls.from_AST(cond_ast)
