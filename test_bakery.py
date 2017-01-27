from atrap import *
from permuta import *

input_set = PermSet.avoiding([Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2))])
#input_set = PermSet.avoiding([Perm((0, 1, 2)), Perm((1, 2, 0))])

bakery = Bakery(input_set, RECIPES)

print(bakery)

bakery.bake(3)
bakery.bake(4)
bakery.bake(5)

bakery.give_me_proof()
