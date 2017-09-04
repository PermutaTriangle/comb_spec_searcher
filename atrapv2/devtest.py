from atrapv2 import TileScope
from atrapv2 import StrategyPacks

basis = "0123_0132_0213_0231_0312_1203_1230_2013_3012"

tilescope = TileScope(basis, **StrategyPacks.binary_pattern_placement)

tree = tilescope.auto_search(1)

tree.get_genf()
