from permuta import *
from grids import Tiling, Block
import sys
from itertools import chain

def tiling_from_mesh_pattern(mpatt, perm_class):
    """Given a mesh pattern and perm_class, generate a tiling where
    the mesh pattern has been placed within the perm class."""
    tiling = {(2*i, 2*j): perm_class
            for i in range(len(mpatt) + 1) for j in range(len(mpatt) + 1) if (i,j) not in mpatt.shading}
    for i in range(len(mpatt)):
        tiling[(2*i + 1, 2*mpatt.pattern[i] + 1)] = Block.point

    return Tiling(tiling)


def is_binary(patt, basis):
    """Checks if a given pattern is binary with respect to the basis"""
    permset = PermSet.avoiding(basis)
    for l in range(len(patt) + 1, 2 * len(patt) + 1):
        for p in permset.of_length(l):
            if patt.count_occurrences_in(p) > 1:
                return False
    return True


def gen_classical_binary(basis, k):
    """Given a basis, generate all classical patterns up to length k that are
    binary under the basis"""
    perm_set = PermSet.avoiding(basis)
    patts = perm_set.of_length(k)
    for length in range(k + 1, 2*k + 1):
        for perm in perm_set.of_length(length):
            patts = list(filter(lambda x: x.count_occurrences_in(perm) < 2,
                patts))
    return patts


def tiling_from_classical_permutation(perm, perm_class):
    """Given a classical pattern and perm_class, generate a tiling where
    the classical pattern has been placed within the perm class."""
    tiling = {(2*i, 2*j): perm_class
            for i in range(len(perm) + 1) for j in range(len(perm) + 1)}
    for i in range(len(perm)):
        tiling[(2*i + 1, 2*perm[i] + 1)] = Block.point

    return Tiling(tiling)

def infer_empty_boxes(patt, basis):
    """Given a permutation pattern, infer the shadable boxes from the basis.
    For every non-shaded box in the pattern, we place a point. If this new
    pattern contains any of the element in the basis, then the box can be
    shaded.
    """
    if isinstance(patt, Perm):
        patt = MeshPatt(patt, {})
    elif not isinstance(patt, MeshPatt):
        raise ValueError("Pattern must be a classical or mesh pattern")

    n = len(patt)
    shadable = list()
    for i in range(n + 1):
        for j in range(n + 1):
            newpatt = patt.add_point((i,j))
            if any(newpatt.pattern.contains(b) for b in basis):
                shadable.append((i,j))
    return patt.shade(shadable)

def filter_maximal(patts):
    last = None
    maximal = list()
    for cur in sorted(patts):
        if cur == last:
            continue
        add = True
        for other in patts:
            if is_subset(cur, other) and cur != other:
                add = False
        if add:
            maximal.append(cur)
        last = cur
    return maximal


def task_to_basis(task):
    return [Perm(map(int, t)) for t in task.split("_")]


def shad_to_binary(shading, length):
    res = 0
    for (x, y) in shading:
        res |= 1 << (x * length + y)
    return res


def is_subset(a, b):
    return (a & ~b) == 0


def flip_binshad_horizontal(binshad, length):
    bits = list(bin(binshad)[2:].zfill(length*length))
    for i in range(len(bits) // length):
        bits[i*length:(i+1)*length] = bits[i*length:(i+1)*length][::-1]
    return int(''.join(bits), 2)


def flip_binshad_vertical(binshad, length):
    bits = list(bin(binshad)[2:].zfill(length*length))
    for i in range(len(bits) // (2*length)):
        bits[i*length:(i+1)*length], bits[(length-i-1)*length:(length-i)*length] = bits[(length-i-1)*length:(length-i)*length], bits[i*length:(i+1)*length]
    return int(''.join(bits), 2)

def count_maximal_binary_patterns(basis, coincidence_classification):
    k = 3
    res = 0
    for patt in PermSet.avoiding(basis).of_length(k):
        if patt not in coincidence_classification:
            continue
        inferred_patt = infer_empty_boxes(patt, basis)
        inferred_patt_bin = shad_to_binary(inferred_patt.shading, len(inferred_patt) + 1)
        cclass = chain.from_iterable(clas for clas in coincidence_classification[patt] if any(is_subset(c, inferred_patt_bin) for c in clas))
        maxibin = filter_maximal(list(filter(lambda x: is_binary(MeshPatt.unrank(patt, x), basis), filter_maximal(cclass))))
        # maxibin = sum(is_binary(MeshPatt.unrank(patt, x), basis) for x in filter_maximal(cclass))
        res += len(maxibin)

        print("{}: Number of  maximal binary patterns: {}".format(patt, len(maxibin)), file=sys.stdout)
    return res

def count_maximal_binary_patterns_from_classical_class(basis, coincidence_classification):
    k = 3
    res = 0
    for patt in PermSet.avoiding(basis).of_length(k):
        if patt not in coincidence_classification:
            continue
        maxibin = sum(is_binary(MeshPatt.unrank(patt, x), basis) for x in filter_maximal(coincidence_classification[patt][0]))
        res += maxibin

        print("{}: Number of maximal binary patterns in classclass: {}".format(patt, maxibin), file=sys.stdout)
    return res
