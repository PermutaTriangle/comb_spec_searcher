from permuta import *
from permuta.permutils import is_insertion_encodable

import sys

def perm_to_str(perm):
    return "".join([str(i) for i in list(perm)])

def perms_to_str(perms):
    return "_".join(perm_to_str(perm) for perm in perms)

with open("length2_test", "w") as f:
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        patts = [ Perm([ int(c) - 1 for c in p ]) for p in line.split('_') ]

        if not is_insertion_encodable(patts):
            print(perms_to_str(patts), file=f)
