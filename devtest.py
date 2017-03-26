from atrap import *
from permuta import *
from grids import *


# mtree = MetaTree(descriptors.Basis([Perm((0,2,1)), Perm((0,1,2,3))]))
mtree = MetaTree(descriptors.Basis([Perm((0,2,1))]))


#mtree.do_level()

print("doing level 1")
mtree.do_level()
mtree.do_level()
mtree.do_level()
mtree.do_level()
