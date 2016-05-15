# Equality pattern rewriting involving a local var of the outer
# query that is a parameter to the inner query. For now we just
# don't perform the rewriting, so as to not mess up the parameter
# info in the symbol table for the inner query.

from incoq.runtime import *

CONFIG(
    default_impl = 'inc',
)

R = Set()
S = Set()

def main():
    for v in [1, 2, 3]:
        R.add(v)
        S.add(v)
    c = 2
    # The c == x clause would cause local x to be replaced by param c
    # in the outer query, and also in the inner query.
    print(sorted(QUERY('Q2', {y for x in R if c == x
                                for y in QUERY('Q1',
                                    {x2 for x2 in S if x2 == x})})))
    # Same, but the inner query appears in a condition clause.
    print(sorted(QUERY('Q5', {x for x in R if c == x
                                if x != QUERY('Q4', max(QUERY('Q3',
                                    {x2 for x2 in S if x2 != x})))})))

if __name__ == '__main__':
    main()
