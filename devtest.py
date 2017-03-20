from atrap import *
from permuta import *
from grids import *


#mtree = MetaTree(Block.decreasing.basis)
#mtree.do_level()

scache = StrategyCache(Block.decreasing.basis)
tiling = Tiling({(0, 0): Block.decreasing})
list(scache.get_equivalence_strategies(tiling))
print("about to do batch strats")
list(scache.get_batch_strategies(tiling))
