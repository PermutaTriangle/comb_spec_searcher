from atrapv2 import TileScope
from atrapv2 import StrategyPacks
from time import time

# basis = "0123_0132_0213_0231_0312_1203_1230_2013_3012"

tilescope = TileScope(basis, **StrategyPacks.binary_pattern_classical_class_placement)

tree = tilescope.auto_search(1)

print(tree.to_json())

# tree.get_genf()
