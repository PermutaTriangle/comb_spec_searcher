from permuta import *
from permuta.permutils import lex_min, is_insertion_encodable

from itertools import combinations

s4 = sorted( PermSet(4) )

def perm_to_str(perm):
    return "".join([str(i) for i in list(perm)])

def perms_to_str(perms):
    return "_".join(perm_to_str(perm) for perm in perms)

for length in range(1, len(s4) + 1):
    with open( "length" + str(length), "w" ) as f:
        for basis in combinations(s4, length):
            if lex_min(basis) == basis:
                if not is_insertion_encodable(basis):
                    task = perms_to_str(basis)

                    print(task, file=f)
    print("finished length {}".format(length))
