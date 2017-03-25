from atrap import *
from permuta import *
from grids import *


mtree = MetaTree(descriptors.Basis([Perm((0,1,2)), Perm((1,0))]))


#mtree.do_level()

print("doing level 1")
mtree.do_level()
mtree.do_level()
mtree.do_level()
mtree.do_level()
mtree.do_level()
print("done")

mtree.find_proof_tree()
