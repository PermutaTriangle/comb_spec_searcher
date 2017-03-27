from atrap import *
from permuta import *
from grids import *


# mtree = MetaTree(descriptors.Basis([Perm((0,2,1)), Perm((0,1,2,3)), Perm((3,2,0,1)), Perm((2,3,0,1))]))

# mtree = MetaTree(descriptors.Basis([Perm((0,1,2,3))]))

mtree = MetaTree(descriptors.Basis([Perm((0,2,1))]))


#mtree.do_level()
mtree.do_level()
mtree.do_level()
mtree.do_level()
mtree.do_level()



# proof_tree = mtree.find_proof_tree()
#
# print( proof_tree.to_json(indent="    ") )
