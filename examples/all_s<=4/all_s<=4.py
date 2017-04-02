from time import time
from atrap import MetaTree
from atrap.strategies import *
from permuta import PermSet
from itertools import combinations
from permuta.permutils import is_finite, lex_min

standard_strategies = [ [all_cell_insertions], [all_point_placements], [subclass_inferral, row_and_column_separation], [reversibly_deletable_cells], [subset_verified, is_empty] ]

finite_strategies = [ [all_cell_insertions, all_minimum_row_placements], [all_equivalent_minimum_row_placements], [empty_cell_inferral, subclass_inferral], [], [subset_verified] ]

def perm_to_str(perm):
    return "".join([str(i) for i in list(perm)])

def perms_to_str(perms):
    return "_".join(perm_to_str(perm) for perm in perms)

all_perms = []

for i in range(2,5):
    all_perms.extend(PermSet(i))

s2 = PermSet(2)

for i in range(len(s2) + 1):
    for s2_subset in combinations(s2, i):
        if lex_min(s2_subset) != s2_subset:
            continue
        s3_perms_available = sorted(PermSet.avoiding(s2_subset).of_length(3))
        for j in range(len(s3_perms_available) + 1):
            for s3_subset in combinations(s3_perms_available, j):
                if s2_subset or s3_subset:
                    if lex_min(s2_subset + s3_subset) != s2_subset + s3_subset:
                        continue
                    s4_perms_available = sorted(PermSet.avoiding(s2_subset + s3_subset).of_length(4))
                    for k in range(len(s4_perms_available) + 1):
                        for s4_subset in combinations(s4_perms_available, k):
                            basis = s2_subset + s3_subset + s4_subset
                            if lex_min(basis) == basis:
                                input_set = PermSet.avoiding(basis)
                                if len(basis) != len(input_set.basis):
                                    continue

                                assert any( len(perm) != 4 for perm in basis )



                                task = perms_to_str(basis)
                                print(task)

                                if is_finite(basis):
                                    strategies = finite_strategies
                                else:
                                    strategies = standard_strategies

                                meta_tree = MetaTree(input_set.basis, *strategies)
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
