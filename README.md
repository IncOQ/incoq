# IncOQ #

IncOQ is a system that takes in a program with high-level queries,
and generates an optimized program that computes the queries
incrementally and in a demand-driven manner.

## Dependencies ##

* `Python 3.4`
* `SimpleStruct 0.2.2` (https://github.com/brandjon/simplestruct)
* `iAST 0.2.1` (https://github.com/brandjon/iast)
* `bintrees 2.0.4` (https://bitbucket.org/mozman/bintrees)
    - (needed for implementing min/max queries; compilation with Cython recommended)

## Invocation ##

Make sure all dependencies are installed or on `PYTHONPATH`. Add this directory
to `PYTHONPATH`. Run as

    python34 -m incoq <input file> <output file> <options>

Use `--help` to see a list of options. Recommended options include

* `--default-impl 'inc'` or `--default-impl 'filtered'` for using
  incrementalization or incrementalization + demand filtering for
  queries by default

* `--auto-query` for treating set comprehensions and calls to `count()`,
  `sum()`, `min()`, and `max()` as queries by default

* `--obj-domain` for translating non-relational queries

Boolean options that are on by default have `--no` prefixed names to disable
them. Both the prefixed and non-prefixed versions are always available anyway,
e.g., to override config information in the input file.

## Running tests ##

    python34 -m unittest discover -t . -s tests/

For running benchmark experiments, see the separate `reproducibility readme.txt`
file (not available on the GitHub distribution of IncOQ).

## Input language ##

The input is a Python module satisfying the following restrictions:

* The line `from incoq.runtime import *` must appears at the top of the file.

* Each update to a queried value must syntactically occurs within the input
  module, i.e., not in an external module (whether it is a library used by the
  input module or a client that uses the input module), and not as a piece of
  dynamically compiled code using `exec()`/`eval()`. An exception is if the
  code performs an update by calling a function in the input module. For
  instance, `exec('s.add(1)')` is not allowed, but `exec('f(s)')`, where `f` is
  a function defined the module and that updates `s` as a side-effect, is okay.

* Each update to a queried value fits one of the allowed forms, below. These
  forms must not be used for updates with incompatible semantics. For instance,
  assigning to a list index using `a[i] = v` is not allowed since it conflicts
  with dictionary assignment, but `a.__setitem__(i, v)` can be used instead.

* All set values that can be queried over should use `incoq.runtime.Set()` in
  place of the built-in python set type. Likewise, dictionaries should use
  `incoq.runtime.Map()`, and objects can optionally `use incoq.runtime.Obj()`.
  (Since we've imported everything from the incoq.runtime namespace, these
  should be addressed as just `Set`, `Map`, and, `Obj`.) This is to ensure that
  all queried values are hashable, have identity semantics, and satisfy our
  dynamic type checks.

The allowed updates are as follows, where `e1`, `e2`, and `e3` are arbitrary
expressions evaluating to `Set`, `Obj`, or `Map` type.

  - `e1.add(e2)`, `e1.remove(e2)`
  
  - `e1.f = e2`, `del e1.f`
  
  - `e1[e2] = e3`, `del e1[e2]`

Updates are strict, meaning that for addition and assignment, the element,
attribute, or key value must not already be present; while for removal and
deletion, the element, attribute, or key value must be present. The following
additional set and map updates are allowed, where strictness is not required.

  - `e.clear()`, `e1.update(e2)`, `e1.intersection_update(e2)`,
    `e1.difference_update(e2)`, `e1.symmetric_difference_update(e2)`,
    `e1.copy_update(e2)`
  
  - `e.dictclear()`, `e.dictcopy_update()`

The meaning of these set updates is the same as in Python. `copy_update()` is
equivalent to `clear` followed by `update`. The dictionary updates are
analogous to `clear()` and `copy_update`.

Note that updates that work by aliasing a method, such as `f = s.add; f(v)`
are not allowed. The same goes for updates to objects via their `__dict__`
attribute. These simply do not fit the required forms.

Set comprehensions are treated as object-set comprehension queries and are
subject to their restrictions: Expressions in these queries must be
deterministic, have no side-effects, and be functions of their free variables
and field/map retrieval expressions. The comprehension should be able to be
evaluated in a left-to-right order (as Python does); this ensures that demand
propagation works, since the implementation always does demand propagation
left-to-right by default.

Aggregate query operands must have the form of an expression allowed on the
right-hand side of a comprehension membership -- i.e., an expression built up
from variables, field retrievals, and map retrievals.

## Relational restrictions ##

If a program is relational, then it can be safely transformed without using the
`--obj-domain` option. A program is relational if the right-hand side of every
comprehension membership, and the operand of every aggregate query, is a
relation variable. A relation variable is a variable with a module-level
declaration of form

    R = Set()

where R is never reassigned, and it is never aliased (in any query or update).
R must hold tuples of uniform arity k, where the left-hand side of each
membership over R is a tuple expression of arity k.

## Annotations ##

Annotations are used to specify transformation configuration options inline
with the source code, and to mark queries.

Global configuration options are declared using the syntax

    CONFIG(
        key=value,
        ...
    )

at module level, where key is an identifier for a configuration option and
value is a Python string literal that can be parsed to a value for that
attribute. Per-symbol configuration options are specified using a similar
construct,

    SYMCONFIG(name
        key=value,
        ...
    )

where name is a Python string literal that is the same as the name of a
variable or query in the program. Valid global and per-symbol options
are listed below.

A set comprehension or aggregate function call expression can be designed as
a query by wrapping it in the QUERY construct, e.g.,

    print({o.f for o in s})

-->

    print(QUERY('Q', {o.f for o in s}))

The string literal 'Q' specifies that the name of this query is Q, and is used
to identify subsequent occurrences of the same query, or to match it with a
SYMCONFIG('Q', ...) annotation.

Alternatively, we can specify that this comprehension is a query using a
module-level annotation:

    QUERY('{o.f for o in s}',
        key=value,
        ...
    )

Here the first argument is a string literal that contains the source
representation of the query to which it applies.

If the `--auto-query` option is used, comprehension and aggregate queries are
determined automatically, so there is no need to add QUERY annotations unless
there's a specific need to customize per-query behavior.

The inline version of QUERY also takes an optional third argument: a dictionary
of annotations that are specific to that query occurrence. Currently the only
supported annotation is `'nodemand'`, which is used to indicate that the values
of the query's parameters are guaranteed to be in the demand set at the program
point where the query occurs, so there's no need to check and add to the demand
set. It is used as

    print(QUERY('Q', {o.f for o in s}, {'nodemand': True}))

## Configuration options ##

Valid global configuration options are as follows. These are also visible by
running `python -m incoq -h`. Note that when written as annotations, the names
of these options use underscores, but on the command line they use dashes
instead. For boolean-valued attributes, use 'true' or 'false' as the value in
the annotations.

* `verbose`: Output information to stdout about how the transformation is
  proceeding. (default: `'false'`)

* `pretend`: Write to stdout instead of the output file. (default: `'false'`)

* `obj_domain`: Use M/F flattening to support nested sets, objects, maps,
  nested tuples, and aliasing. Usually a good idea unless you know that your
  program is relational. (default: `'false'`)

* `default_impl`: Default implementation strategy to use for queries, if not
  overridden on a per-query basis. Allowed values are:
  
    - `'normal'`: Do not incrementalize. (default)
    
    - `'aux'`: For a comprehension, recompute the result whenever it is
      requested, but do so using incrementally maintained auxiliary maps.
      For an aggregate, do not incrementalize.
    
    - `'inc'`: Compute incrementally.
    
    - `'filtered': For a comprehenesion, compute incrementally with demand
      filtering. For an aggregate, compute incrementally.

* `default_demand_set_maxsize`: For queries using a demand set, a positive
  integer value indicating the maximum size of the demand set, or `'none'` to
  indicate no limit (the default). If set to 1, the demand set will be cleared
  each time a query over a new combination of parameter values is performed.
  If set to any other integer, an LRU cache of that size is used to evict the
  least-recently-used entry whenever the limit would be exceeded.

* `use_singletag_demand`: When using demand filtering, allow only one tag for
  each variable. (default: `'false'`)

* `unwrap_singletons`: Rewrite some uses of singletons in the output program
  to eliminate the unnecessary tuple packing/unpacking. (default: `'true'`)

* `auto_query`: Wrap set comprehensions and aggregates in QUERY constructs
  automatically; usually a good idea. (default: `'true'`)

* `inline_maint_code`: Inline the generated functions containing invariant
  maintenance code. (default: `'false'`)

* `elim_counts`: Enable counting elimination globally (where safe). (default:
  `'true'`)

* `elim_dead_relations`: Eliminate relations that have no uses in the final
  program. (default: `'true'`)

* `elim_type_checks`: Enable type check elimination globally (where safe).
  (default: `'true'`)

* `elim_dead_funcs`: Eliminate uncalled maintenance functions. (default:
  `'true'`)

* `distalgo_mode`: Enable special rewritings for the DistAlgo inc interface;
  currently all this does is allow `len()` calls to be treated as the `count()`
  aggregate query. (default: `'true'`)

* `typedefs`: A string of the form `name1=typeexpr1; ...; nameN=typeexprN`,
  where each typeexpr is a type expression string that can be evaluated by
  incoq/compiler/type/types.py's eval_typestr() function. Used to define
  aliases for types that will be passed in for individual symbols.

* `costs`: Perform cost analysis and emit cost comments at the top of each
  non-recursive function in the output program. (default: `'true'`)

Valid per-symbol query options are as follows. These can only be entered in
through a program annotation (or when calling the compiler's invoke() method
from a Python script), not through the command line.

* `params`: A comma-separated list of parameter identifiers. If not supplied,
  parameters are inferred automatically based on Python-like scoping rules.

* `impl`: Implementation strategy to use for this query. Valid values are the
  same as for `default_impl`, above.

* `demand_param_strat`: Strategy for deciding which parameters are considered
  demand parameters. One of `'unconstrained'` (default), `'all'`, or
  `'explicit'`. If `'explicit'` is used then the particular demand parameters
  should be supplied as a comma separated list of identifiers for the
  `demand_params` option; otherwise that option should be left alone.

* `demand_set_maxsize`: Integer or `'none'`, as for the global option above.

* `clause_reorder`: Normally, the demand strategy propagates demand
  left-to-right. This option can be set to a comma-separated sequence of
  integers indicating a permutation to apply to the comprehension's clauses
  before determining this left-to-right order. For instance, setting it to
  `'3, 1, 2'` causes demand to propagate through the third clause, then the
  first, then the second.

* `count_elim_safe_override`: Whether to apply counting elimination (if
  the global `elim_counts` option is enabled) even if it isn't otherwise
  known to be safe for this query.

* `well_typed_data`: Whether the demanded parameter values for this query
  are guaranteed to be well-typed (with respect to some safe typing). If
  `'true'`, type check elimination will be performed for this query if it
  is implemented using demand filtering.
