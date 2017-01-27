import atrap
from permuta import *

#input_set = PermSet.avoiding([Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2))])
#input_set = PermSet.avoiding([Perm((0, 1, 2)), Perm((1, 2, 0))])
#input_set = PermSet.avoiding([
#                               Perm((0, 1, 2, 3)),
#                               Perm((1, 2, 3, 0)),
#                               Perm((1, 3, 2, 0)),
#                               Perm((2, 3, 0, 1)),
#                            ])
#input_set = PermSet.avoiding([
#                               Perm((0, 1, 2, 3)),
#                               Perm((2, 3, 1, 0)),
#                            ])
#input_set = PermSet.avoiding([Perm((0, 1, 2)), Perm((1, 2, 0))])
#input_set = PermSet.avoiding([Perm((1, 0)), Perm((0, 1, 2))])
input_set = PermSet.avoiding([Perm((0, 1)), Perm((1, 0))])

bakery = atrap.bakery_naive.Bakery(input_set)
#recipes = [atrap.recipes.all_row_and_column_insertions]
#bakery = atrap.bakery_naive.Bakery(input_set, recipes)

print(bakery)

for _ in range(5):
    good = bakery.bake()
    if good:
        bakery.give_me_proof()
        break
