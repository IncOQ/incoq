"""Masks for pattern-based set retrieval."""

"""
A mask is the structure underlying a tuple pattern. A mask with
k parts can be applied to a tuple or relation of arity k. In the
basic case, each part is either 'b' or 'u' indicating "bound" or
"unbound" respectively. Given a mask and a key that consists of
values for each bound part, a pattern match returns the values
for each unbound part in the corresponding tuple(s).

A wildcard part is represented by 'w'. It acts as 'u', but its
corresponding value is not returned as part of the match.

An equality part is an integer (represented here as a decimal
string). It identifies the index of a previous part (starting at 1)
that this part must equal. Equality parts do not have corresponding
entries in the key.

Example match:

  Mask:  bubw12u
  Key:   (a, c)
  Tuple: (a, b, c, d, a, b, z)
  Result: (b, z)

"""

### TODO: document keymasks


__all__ = [
    'Mask',
    'AuxmapSpec',
]


from simplestruct import Struct, Field
from simplestruct.type import checktype, checktype_seq

import oinc.compiler.incast as L


class Mask(Struct):
    
    """Pattern mask."""
    
    parts = Field()
    
    @classmethod
    def from_vars(cls, vars, bindenv, wildvars=None):
        """Construct the mask underlying a variable pattern tuple
        with a given environment of bound variables.
        
        vars is a sequence of variable identifiers, or '_' for
        wildcards. bindenv is a set of variables that are considered
        bound. The returned mask can be used with the bound variables
        to obtain matching values for the unbound variables.
        
        If wildcars is given, it must be disjoint from bindenv.
        Variables in wildvars will be replaced by wildcards.
        """
        parts = []
        for i, v in enumerate(vars):
            if v == '_':
                parts.append('w')
            elif v in vars[:i]:
                n = vars.index(v) + 1
                parts.append(str(n))
            elif v in bindenv:
                parts.append('b')
            elif wildvars is not None and v in wildvars:
                parts.append('w')
            else:
                parts.append('u')
        
        return cls(parts)
    
    @classmethod
    def from_proj(cls, vars):
        """Construct a projection mask from a sequence of variables
        and wildcard symbols.
        """
        parts = []
        for i, v in enumerate(vars):
            if v == '_':
                parts.append('w')
            else:
                parts.append('b')
        
        return cls(parts)
    
    @classmethod
    def from_keylen(cls, n):
        """Construct a keymask with n many parameter parts."""
        return cls('b' * n + 'u')
    
    def __new__(cls, parts):
        """Construct from a string, or a sequence of strings."""
        # Validate parts.
        try:
            checktype(parts, str)
        except TypeError:
            checktype_seq(parts, str)
        parts = tuple(parts)
        
        if not all(c == 'b' or
                   c == 'u' or
                   (c.isdigit() and c != '0') or
                   c == 'w'
                   for c in parts):
            raise ValueError('Invalid pattern mask: ' + ''.join(parts))
        
        if any(c.isdigit() and len(c) > 1
               for c in parts):
            raise ValueError('Equality constraints with index > 9 '
                             'not supported')
        
        if any(c.isdigit() and int(c) - 1 >= i
               for i, c in enumerate(parts)):
            raise ValueError('Equality constraint must refer to smaller '
                             'index than own occurrence')
        
        return super().__new__(cls, parts)
    
    def __init__(self, parts):
        # Set derived data.
        
        if self.parts == ('b', 'u'):
            self.maskstr = 'out'
        elif self.parts == ('u', 'b'):
            self.maskstr = 'in'
        else:
            self.maskstr = ''.join(self.parts)
        """String (possibly non-formulaic) representation of mask.
        Valid for use as an identifier.
        """
        
        self.is_allbound = all(c == 'b' or c.isdigit()
                               for c in self.parts)
        """True if fully bound. Equality-constrained parts count as
        bound.
        """ 
        
        self.is_allunbound = all(c == 'u' or c == 'w'
                                 for c in self.parts)
        """True if fully unbound. Wildcards count as unbound."""
        
        self.has_wildcards = any(c == 'w' for c in self.parts)
        """True if there are wildcards."""
        
        self.has_equalities = any(c.isdigit()
                                  for c in self.parts)
        """True if there are any equalities."""
        
        self.is_mixed = not(self.is_allbound or self.is_allunbound)
        """True if neither fully bound nor unbound."""
        
        
        p = self.parts
        n = len(p)
        self.is_keymask = (all(c == 'b' for c in p[:n-1]) and
                           p[n-1] == 'u')
        """True if has form bbb...bu."""
        
        # Lookup mask: True if has form bbb...bu...uuu.
        if 'u' in p:
            first_u = p.index('u')
            self.is_lookupmask = (all(c == 'b' for c in p[:first_u]) and
                                  all(c == 'u' for c in p[first_u:]))
            self.lookup_arity = first_u
        else:
            self.is_lookupmask = False
            self.lookup_arity = None
    
    def __str__(self):
        return self.maskstr
    
    def __repr__(self):
        return type(self).__name__ + '(' + self.maskstr + ')'
    
    def __len__(self):
        return len(self.parts)
    
    def make_node(self):
        """Return a Str node with the mask string."""
        # Would break if we allowed equality indices > 9.
        return L.Str(''.join(self.parts))
    
    def split_vars(self, vars):
        """Given a sequence of variables, determine which ones are
        bound and unbound according to this pattern.
        
        Return a triple of a tuple of bound vars, a tuple of unbound
        vars, and a tuple of equality pairs that are necessary and
        sufficient to satisfy the equality constraints.
        
        Variables corresponding to bound components and unbound
        components are appended to the respective lists. Variables
        corresponding to wildcard and equality parts are skipped.
        """
        if len(vars) != len(self.parts):
            raise ValueError('Variable list of wrong length ({}) '
                             'for mask ({})'.format(
                             len(vars), len(self.parts)))
        
        boundvars = []
        unboundvars = []
        eqs = []
        for v, c in zip(vars, self.parts):
            if c == 'b':
                boundvars.append(v)
            elif c == 'u':
                unboundvars.append(v)
            elif c.isdigit():
                n = int(c) - 1
                eqs.append((vars[n], v))
            elif c == 'w':
                pass
        
        return tuple(boundvars), tuple(unboundvars), tuple(eqs)
    
    def make_projkey(self, val):
        """If this mask has no 'u' components, given a value for a tuple,
        construct a key expression out of the non-wildcard components.
        """
        components = []
        for i, c in enumerate(self.parts):
            if c == 'b':
                # val[i]
                expr = L.Subscript(val, L.Index(L.Num(i)), L.Load())
                components.append(expr)
            elif c == 'w':
                pass
            elif c.isdigit():
                pass
            else:
                assert()
        return L.tuplify(components)
    
    def breakkey(self, node):
        """For a keymask, break a key node into a tuple of its parts."""
        assert self.is_keymask
        
        n = len(self.parts) - 1
        if n == 1:
            return (node,)
        else:
            assert(isinstance(node, L.Tuple))
            assert(len(node.elts) == n)
            return node.elts
    
    def make_delta_mask(self):
        """Form a new mask for using a delta check on this key.
        Replace all 'u' with 'b', leaving other parts alone.
        """
        new_parts = []
        for c in self.parts:
            if c == 'u':
                new_parts.append('b')
            else:
                new_parts.append(c)
        return Mask(new_parts)
    
    def make_param_proj_mask(self):
        """Form a new mask that projects out everything that's
        not a bound (not counting equality components). E.g.
        turn 'bbuw' into 'uuww'.
        """
        new_parts = []
        for c in self.parts:
            if c == 'b':
                new_parts.append('u')
            else:
                new_parts.append('w')
        return Mask(new_parts)
    
    def make_interkey_mask(self, vars, bindenv):
        """Form a new mask that goes from one partition of given key
        values to the other partition of remaining key values. vars is
        a list of variable names of length equal to the number of bound
        components in this mask -- i.e. keys. bindenv is a set of key
        vars that are to be considered bound for the purposes of the
        new mask. The resulting mask goes form the vars that are
        in bindenv, to the vars that are not in bindenv, relative to
        the same relation as the one that this current mask indexes.
        Notably, equality and wildcards in this mask are preserved
        into the new mask.
        
        Put another way: Let m1 be a mask with key variables (bound
        positions) K. Let B be those variables of K that are also in
        the bindenv, and let m2 be formed by calling this function on
        m1 with bindenv. Then the result of matching m2 with B in a
        relation R should be the set of all values for key variables
        in K - B, such that the result of matching m1 with B and those
        values over R is non-empty. 
        """
        assert len(vars) == len([c for c in self.parts if c == 'b'])
        
        out_parts = []
        
        it = iter(vars)
        for c in self.parts:
            # A key position ('b') stays bound if it is in bindenv,
            # or else becomes an unbound.
            if c == 'b':
                v = next(it)
                if v in bindenv:
                    out_parts.append('b')
                else:
                    out_parts.append('u')
            # Unbounds become wildcards. Wildcards stay wildcards.
            elif c in ['u', 'w']:
                out_parts.append('w')
            # Equality constraints stay the same.
            elif c.isdigit():
                out_parts.append(c)
            else:
                assert()
        
        return Mask(out_parts)


# Common instances.
Mask.BB = Mask('bb')
Mask.OUT = Mask('bu')
Mask.IN = Mask('ub')
Mask.UU = Mask('uu')
Mask.B1 = Mask('b1')
Mask.BW = Mask('bw')
Mask.U = Mask('u')


class AuxmapSpec(Struct):
    
    rel = Field(str)
    mask = Field(Mask)
    
    def __init__(self, rel, mask):
        self.lookup_name = '{}_{}'.format(self.rel, self.mask.maskstr)
        self.map_name = '_m_' + self.lookup_name
    
    def __str__(self):
        return self.lookup_name
