from atrapv2 import TileScope
from atrapv2 import StrategyPacks
from comb_spec_searcher.visual_queue import VisualQueue

from comb_spec_searcher import StrategyPack

from itertools import chain

def to_vis_pack(pack):
    total_strats = list(chain(*pack.other_strats))
    print(total_strats)
    return StrategyPack(
        name=pack.name,
        ver_strats=pack.ver_strats,
        inf_strats=pack.inf_strats,
        eq_strats=pack.eq_strats,
        other_strats=[total_strats],
    )


visual_pack = to_vis_pack(StrategyPacks.point_placement)

tilescope = TileScope("012", visual_pack, objectqueue=VisualQueue)
#tilescope = TileScope("012", visual_pack, objectqueue=VisualQueue, forward_equivalence=True)
proof_tree = tilescope.auto_search(cap=1)
proof_tree.pretty_print()
print(proof_tree.to_json())
input()
