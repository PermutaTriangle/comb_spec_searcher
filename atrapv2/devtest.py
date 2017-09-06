from atrapv2 import TileScope
from atrapv2 import StrategyPacks
from time import time

# basis = "0123_0132_0213_0231_0312_1203_1230_2013_3012"

# basis = "0132_0231_1032_2031"

basis = "1302_2031"

start = time()

strategy_pack = StrategyPacks.row_and_column_placements_w_symm
strategy_pack["non_interleaving_recursion"] = True
tilescope = TileScope(basis, **strategy_pack)

print("We took advantage of " + str(len(tilescope.symmetry)) + " symmetries")

tree = tilescope.auto_search(1)


tree.pretty_print()
print(tree.to_json())

tree = tilescope.get_proof_tree()
print("There were " + str(tilescope.recursively_expanded) + " expanded by decomposition.")
print("There were " + str(tilescope.expanded_tilings) + " full expanded tilings.")
end = time()

print("Time taken was " + str(end - start) + " seconds")

# while not tree is None:
#     try:
#         tree.get_genf()
#         break
#     except:
#         print("Trying to find another tree")
#         tree.pretty_print()
#         print(tree.to_json())
        # tree = tilescope.get_proof_tree()
