from atrapv2 import TileScope
from atrapv2 import StrategyPacks
from time import time

# basis = "0123_0132_0213_0231_0312_1203_1230_2013_3012"

# basis = "0132_0231_1032_2031"

basis = "1302_2031"

start = time()

tilescope = TileScope(basis, **StrategyPacks.row_and_column_placements)
print(len(tilescope.symmetry))

tree = tilescope.auto_search(1)


tree.pretty_print()
print(tree.to_json())

tree = tilescope.get_proof_tree()
print(len(tilescope.tilingdb.label_to_info))
print(tilescope.expanded_tilings)
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
