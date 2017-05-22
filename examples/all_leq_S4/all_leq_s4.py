from permuta import PermSet
from itertools import combinations
from permuta.permutils import is_finite, lex_min

def perm_to_str(perm):
    return "".join([str(i) for i in list(perm)])

def perms_to_str(perms):
    return "_".join(perm_to_str(perm) for perm in perms)

all_perms = []

for i in range(2,5):
    all_perms.extend(PermSet(i))

s2 = PermSet(2)

with open('all_leq_S4', 'w') as f:
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
                            # if k >=4:
                            #     continue
                            for s4_subset in combinations(s4_perms_available, k):
                                basis = s2_subset + s3_subset + s4_subset
                                if lex_min(basis) == basis:
                                    input_set = PermSet.avoiding(basis)
                                    if len(basis) != len(input_set.basis):
                                        continue

                                    assert any( len(perm) != 4 for perm in basis )

                                    task = perms_to_str(basis)
                                    print(task, file=f)

                                    # if is_finite(basis):
                                    #     strategies = finite_strategies_w_min_row
                                    # else:
                                    #     continue
                                    #     strategies = standard_strategies
