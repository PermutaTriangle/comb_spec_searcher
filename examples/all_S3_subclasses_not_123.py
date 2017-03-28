from time import time
from atrap import MetaTree
from atrap.strategies import subclass_inferral, subset_verified
from permuta import Perm
from permuta import *
from permuta.misc.symmetry import *
from itertools import combinations

perms = []
for i in range(2,4):
    perms.extend(PermSet(i))


def perm_to_str(perm):
    return "".join([str(i) for i in list(perm)])

def perms_to_str(perms):
    return "_".join(perm_to_str(perm) for perm in perms)

for i in range(1, len(perms) + 1):
    for basis in combinations(perms,i):
        if len(basis) == 1:
            if Perm((0,1,2)) in basis or Perm((2,1,0)) in basis:
                continue
        if lex_min(basis) == basis:
            input_set = PermSet.avoiding(basis)
            if len(basis) != len(input_set.basis):
                continue

            meta_tree = MetaTree(input_set.basis, inferral_strategies=[subclass_inferral], verification_strategies=[subset_verified])

            task = perms_to_str(basis)
            print(task)
            start_time = time()

            while not meta_tree.has_proof_tree():
                meta_tree.do_level()


            with open(task, "w") as f:
                proof_tree = meta_tree.find_proof_tree()
                print("",file=f)
                print("Finding the proof tree for", input_set.__repr__() ,  "took", int(time() - start_time), "seconds",file=f)
                print("",file=f)
                print("Human readable:",file=f)
                print("",file=f)

                proof_tree.pretty_print(file=f)

                print("",file=f)
                print("Computer readable (JSON):",file=f)
                print("",file=f)
                print(proof_tree.to_json(indent="    ", sort_keys=True), file=f)
