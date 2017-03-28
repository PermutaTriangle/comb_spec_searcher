from atrap import MetaTree
from permuta import Perm

from time import time
from atrap.strategies import subset_verified

# mtree = MetaTree(descriptors.Basis([Perm((0,2,1)), Perm((0,1,2,3)), Perm((3,2,0,1)), Perm((2,3,0,1))]))

# mtree = MetaTree(descriptors.Basis([Perm((0,1,2,3))]))

# mtree = MetaTree(descriptors.Basis([Perm((0,2,1))]))

# mtree = MetaTree(descriptors.Basis([Perm((0,1))]))

mtree = MetaTree([Perm((0,1,2)), Perm((0,2,1))])

# mtree = MetaTree([])



#mtree.do_level()
start = time()

mtree.do_level()
mtree.do_level()
mtree.do_level()
mtree.do_level()
mtree.do_level()

end = time()

print("I took", end - start, "seconds")






# proof_tree = mtree.find_proof_tree()
#
# print( proof_tree.to_json(indent="    ") )
