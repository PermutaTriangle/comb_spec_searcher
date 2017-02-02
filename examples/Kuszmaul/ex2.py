import atrap
from permuta import *

# I let this one run for a while but it did not finish. I think it needs
# a pattern insertion into a cell; a generalization of point cell insertion,
# because Struct found the cover
#
# 00000000000000000000000000000000000000000000000000000000000000000000000000000000000011111000000000000000000000000000000000000000000000000000000000000000000000000000011000000000000000000000000100000000100000
#
# +-+-+-+-+
# | |o| | |
# +-+-+-+-+
# | | | |o|
# +-+-+-+-+
# |o| | | |
# +-+-+-+-+
# | | |1| |
# +-+-+-+-+
# 1: Av([[1, 3, 2]])
#
# 16623:
# 11111111111111111111111111111111111111111111111111111111111111111111111111111111111100000111111111111111111111111111111111111111111111111111111111111111111111111111100111111111111111111111111011111111011111
#
# +-+
# |1|
# +-+
# 1: Av([[1, 3, 2]])
# 
# Notice that 132 is a binary mesh pattern with respect to this basis



task = '2431_2143_3142_4132_1432_1342_1324_1423_1243'
patts = [ Perm([ int(c)-1 for c in p ]) for p in task.split('_') ]
input_set = PermSet.avoiding(patts)

#recipes = [atrap.recipes.all_row_and_column_insertions]
recipes = [atrap.recipes.all_cell_insertions]
bakery = atrap.bakery_naive.Bakery(input_set, recipes)

#bakery = atrap.bakery_naive.Bakery(input_set)

print("Finding proof for:\n")
print(input_set)
print()
print(bakery)

while True:
    good = bakery.bake()
    if good:
        bakery.give_me_proof()
        break
