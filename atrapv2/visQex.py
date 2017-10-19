from atrapv2 import TileScope
from atrapv2 import StrategyPacks
from atrapv2 import VisualQueue

tilescope = TileScope("012_120", StrategyPacks.point_placement, objectqueue=VisualQueue)
proof_tree = tilescope.auto_search(cap=1)
proof_tree.pretty_print()
print(proof_tree.to_json())
