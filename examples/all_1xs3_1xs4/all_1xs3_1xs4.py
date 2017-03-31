from time import time
from atrap import MetaTree
from atrap.strategies import *
from permuta import *
from permuta.misc.symmetry import *
from itertools import combinations

def perm_to_str(perm):
    return "".join([str(i) for i in list(perm)])

def perms_to_str(perms):
    return "_".join(perm_to_str(perm) for perm in perms)

standard_strategies = [ [all_cell_insertions, all_row_placements], [all_point_placements], [empty_cell_inferral, subclass_inferral, row_and_column_separation], [reversibly_deletable_cells], [subset_verified, is_empty] ]

for perm1 in PermSet(3):
    for perm2 in PermSet(4):
        basis = (perm1, perm2)
        if lex_min(basis) == basis:
            input_set = PermSet.avoiding(basis)
            if len(basis) != len(input_set.basis):
                continue
            task = perms_to_str(basis)
            print(task)
            start = time()

            meta_tree = MetaTree(basis, *standard_strategies)

            while not meta_tree.has_proof_tree():
                meta_tree.do_level()

            proof_tree = meta_tree.find_proof_tree()

            with open(task, "w") as f:
                print("",file=f)
                print("Finding the proof tree for", input_set.__repr__() ,  "took", int(time() - start), "seconds",file=f)
                print("",file=f)
                print("Human readable:",file=f)
                print("",file=f)

                proof_tree.pretty_print(file=f)

                print("",file=f)
                print("Computer readable (JSON):",file=f)
                print("",file=f)
                print(proof_tree.to_json(indent="    ", sort_keys=True), file=f)
