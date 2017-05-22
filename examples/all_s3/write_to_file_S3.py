from itertools import combinations

from permuta import *
from permuta.permutils import *

perms = tuple(PermSet(3))
def perm_to_str(perm):
    return "".join([str(i) for i in list(perm)])

def perms_to_str(perms):
    return "_".join(perm_to_str(perm) for perm in perms)

with open('all_S3', 'w') as f:

    for i in range(1, len(perms)):
        for basis in combinations(perms,i):
            if lex_min(basis) == basis:
                input_set = PermSet.avoiding(basis)
                if len(basis) != len(input_set.basis):
                    continue

                task = perms_to_str(basis)
                print(task, file=f)
