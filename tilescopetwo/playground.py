from comb_spec_searcher import ProofTree
from tilescopetwo import TileScopeTWO, StrategyPacks
from tilescopetwo.strategies import empty_cell_inferral

from grids_two import Tiling, Obstruction
from permuta import Perm
import json


basis = '0132_0213_0231_1023_1230_2013_3012'

tilescope = TileScopeTWO(basis=basis,
                         strategy_pack=StrategyPacks.forced_patterns_2_basic,
                         compress=True,
                         interleaving_decomposition=False)

tree = tilescope.auto_search(cap=1, status_update=60, verbose=True)

jsonable = tree.to_jsonable()

print(jsonable)

print()

dumped = json.dumps(jsonable)

print(dumped)

recovered_tree = ProofTree.from_json(dumped)

print(tree == recovered_tree)
