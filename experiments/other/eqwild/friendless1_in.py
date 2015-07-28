from incoq.runtime import *

OPTIONS(
    obj_domain = True,
)


bob = Obj()
bob.name = 'bob'
bob.friends = Set()

sally = Obj()
sally.name = 'sally'
sally.friends = Set()

bob.friends.add(sally)

fred = Obj()
fred.name = 'fred'
fred.friends = Set()
fred.friends.add(fred)

S = Set()
S.add(bob)
S.add(sally)

print(sorted({user for user in S for someone in user.friends}))
