from atrap import *
from permuta import *
from grids import *


mtree = MetaTree(descriptors.Basis([Perm((0,2,1))]))


#mtree.do_level()

print("doing level 1")
mtree.do_level()

mtree.do_level()

mtree.do_level()

mtree.do_level()

mtree.do_level()

mtree.find_proof_tree()
