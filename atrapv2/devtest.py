from atrapv2 import TileScope
from atrap import StrategyPacks

basis = "012"

tilescope = TileScope(basis, **StrategyPacks.row_and_column_insertion)

tilescope.auto_search(1)

1 in tilescope.tilingdb
