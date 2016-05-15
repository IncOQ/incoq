"""Tag and filter structures."""


__all__ = [
    'Filter',
    'Tag',
    'StructureGenerator',
]


from collections import defaultdict
from simplestruct import Struct, TypedField

from incoq.compiler.incast import L
from incoq.compiler.symbol import N
from incoq.compiler.comp import Kind


class Filter(Struct):
    _immutable = False
    
    i = TypedField(int)
    """Index of clause for which this filter is generated."""
    name = TypedField(str)
    """Name of this filter."""
    clause = TypedField(L.clause)
    """Clause that this filter is based on."""
    preds = TypedField(str, seq=True)
    """Names of predecessor tags for this filter."""


class Tag(Struct):
    _immutable = False
    
    i = TypedField(int)
    """Index of clause for which this tag is generated."""
    name = TypedField(str)
    """Name of this tag."""
    tag_var = TypedField(str)
    """Query variable controlled by this tag."""
    clause = TypedField(L.clause)
    """Clause that this tag projects."""


class StructureGenerator:
    
    # The process is broken up into several phases, each in their own
    # method. First we create Tag and Filter structures in the structs
    # attribute and its indices. Then we simplify tag and filter names
    # where possible. Next we produce comprehensions for the structures.
    
    def __init__(self, symtab, comp, query_name):
        self.symtab = symtab
        assert isinstance(comp, L.Comp)
        self.comp = comp
        self.query_name = query_name
        
        # All tags and filters, in definition order (i.e., left-to-right
        # with respect to the original query comprehension).
        self.structs = []
        
        self.init_indices()
    
    def init_indices(self):
        """Initialize/reset indices over structures."""
        self.filters = []
        self.filters_by_rel = defaultdict(lambda: [])
        self.filters_by_pred = defaultdict(lambda: [])
        self.filters_by_i = {}
        self.clause_over_filter = {}
        self.tags = []
        self.tags_by_var = defaultdict(lambda: [])
        self.tags_by_i = defaultdict(lambda: [])
        self.tags_by_name = {}
    
    def maint_indices_for_add(self, struct):
        """Maintain all indices when a new tag or filter structure
        is appended.
        """
        ct = self.symtab.clausetools
        
        if isinstance(struct, Filter):
            filter = struct
            self.filters.append(filter)
            rel = ct.rhs_rel(filter.clause)
            self.filters_by_rel[rel].append(filter)
            for p in filter.preds:
                self.filters_by_pred[p].append(filter)
            assert filter.i not in self.filters_by_i
            self.filters_by_i[filter.i] = filter
            assert filter.name not in self.clause_over_filter
            self.clause_over_filter[filter.name] = \
                self.change_rhs(filter.clause, filter.name)
        
        elif isinstance(struct, Tag):
            tag = struct
            self.tags.append(tag)
            self.tags_by_var[tag.tag_var].append(tag)
            self.tags_by_i[tag.i].append(tag)
            assert tag.name not in self.tags_by_name
            self.tags_by_name[tag.name] = tag
        
        else:
            assert()
    
    def add_struct(self, struct):
        """Add a new structure and maintain indices."""
        self.structs.append(struct)
        self.maint_indices_for_add(struct)
    
    def recompute_indices(self):
        """Recompute all indices for arbitrary changes to structures."""
        self.init_indices()
        for struct in self.structs:
            self.maint_indices_for_add(struct)
    
    def get_filter_name(self, rel, n):
        return N.get_filter_name(self.query_name, rel, n)
    
    def get_tag_name(self, var, n):
        return N.get_tag_name(self.query_name, var, n)
    
    def get_preds(self, i, in_vars):
        """Return the names of all tags defined for clauses lower than
        clause i, over any of the variables listed in in_vars.
        
        If the use_singletag_demand config option is True, only return
        the last applicable tag.
        """
        result = []
        for v in in_vars:
            for t in self.tags_by_var[v]:
                if not t.i < i:
                    continue
                result.append(t.name)
        
        if self.symtab.config.use_singletag_demand:
            result = result[:1]
        
        return result
    
    def change_rhs(self, cl, query_name):
        """Generate a new clause whose RHS rel is the name of a result
        set over the given query name.
        """
        ct = self.symtab.clausetools
        rel_name = N.get_resultset_name(query_name)
        return ct.rename_rhs_rel(cl, lambda x: rel_name)
    
    def make_structs(self):
        """Populate the structures based on the comprehension."""
        assert len(self.structs) == 0
        ct = self.symtab.clausetools
        
        # Generate for each clause.
        for i, cl in enumerate(self.comp.clauses):
            if ct.kind(cl) is not Kind.Member:
                continue
            
            vars = ct.lhs_vars(cl)
            in_vars = ct.tagsin_lhs_vars(cl)
            out_vars = ct.tagsout_lhs_vars(cl)
            rel = ct.rhs_rel(cl)
            if rel is None:
                raise L.TransformationError('Cannot generate tags and filter '
                                            'for clause: {}'.format(cl))
            
            # Generate a filter for this clause.
            if i != 0:
                n = len(self.filters_by_rel[rel]) + 1
                name = self.get_filter_name(rel, n)
                preds = self.get_preds(i, in_vars)
                if ct.filter_needs_preds(cl) and len(preds) == 0:
                    raise L.ProgramError('No predecessors tags for filter '
                                         'over clause: {}'.format(
                                         L.Parser.ts(cl)))
                filter = Filter(i, name, cl, preds)
                self.add_struct(filter)
                filtered_cl = self.clause_over_filter[name]
            else:
                # First clause acts as its own filter; no new structure.
                filtered_cl = cl
            
            # Generate a tag for each variable on the LHS.
            for var in out_vars:
                n = len(self.tags_by_var[var]) + 1
                name = self.get_tag_name(var, n)
                tag = Tag(i, name, var, filtered_cl)
                self.add_struct(tag)
    
    def simplify_names(self):
        """Remove numbers from structure names, when not ambiguous."""
        ct = self.symtab.clausetools
        
        # Not that indices will temporarily become stale while
        # we're changing names around.
        
        for filter in self.filters:
            rel = ct.rhs_rel(filter.clause)
            if len(self.filters_by_rel[rel]) == 1:
                name = self.get_filter_name(rel, None)
                filter.name = name
                # Update linked tags.
                for tag in self.tags_by_i[filter.i]:
                    tag.clause = self.change_rhs(tag.clause, name)
        
        for tag in self.tags:
            if len(self.tags_by_var[tag.tag_var]) == 1:
                old_name = tag.name
                name = self.get_tag_name(tag.tag_var, None)
                tag.name = name
                # Update linked filters.
                for filter in self.filters_by_pred[old_name]:
                    filter.preds = [name if t == old_name else t
                                    for t in filter.preds]
        
        self.recompute_indices()
    
    def prune_tags(self):
        """Delete unused tags."""
        to_prune = []
        for tag in self.tags:
            filters = self.filters_by_pred[tag.name]
            if len(filters) == 0:
                to_prune.append(tag)
        
        for tag in to_prune:
            self.structs.remove(tag)
        
        self.recompute_indices()
    
    def make_comp(self, struct):
        """Return the Comp node corresponding to a structure."""
        ct = self.symtab.clausetools
        resname = N.get_resultset_name
        
        if isinstance(struct, Filter):
            filter = struct
            vars = ct.lhs_vars(filter.clause)
            pred_clauses = []
            for t in filter.preds:
                tag = self.tags_by_name[t]
                pred_cl = L.RelMember([tag.tag_var], resname(tag.name))
                pred_clauses.append(pred_cl)
            return L.Comp(L.tuplify(vars), pred_clauses + [filter.clause])
        
        elif isinstance(struct, Tag):
            tag = struct
            return L.Comp(L.tuplify([tag.tag_var]), [tag.clause])
        
        else:
            assert()
    
    def make_filter_list(self):
        """Get the list of filtered clauses corresponding to the query's
        clauses, accounting for the fact that some clauses are their own
        filters (e.g. the U-set clause).
        """
        result = []
        clauses = self.comp.clauses
        for i in range(len(clauses)):
            if i in self.filters_by_i:
                filter = self.filters_by_i[i]
                result.append(self.clause_over_filter[filter.name])
            else:
                result.append(clauses[i])
        return result
