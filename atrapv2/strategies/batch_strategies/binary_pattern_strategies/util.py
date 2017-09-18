from permuta import *
from permuta.misc import *
from grids import Tiling, Block
import sys
from itertools import chain, permutations, product

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


def make_force_strength_func(force):
    def keyfunc(occ, patt):
        return [
            -occ[i] if d == DIR_WEST else
            occ[i] if d == DIR_EAST else
            -patt[occ[i]] if d == DIR_SOUTH else
            patt[occ[i]] for (i,d) in force]
    return keyfunc


def is_binary_force(patt, force, basis=[]):
    """Given a classical pattern patt and a force, checks if the pattern is
    binary with respect to the force and the basis."""
    permset = PermSet.avoiding(basis)
    perms = chain.from_iterable(permset.of_length(i) for i in range(len(force), 2*len(patt) - len(force) + 1))
    force_strength = make_force_strength_func(force)
    for p in perms:
        forced = [force_strength(occ, p) for occ in patt.occurrences_in(p)]
        if len(forced) > 0:
            if forced.count(min(forced)) > 1:
                return False
    return True

def force_backtrack(patt, cur_force, at_index, basis):
    if at_index < len(patt):
        for f in force_backtrack(patt, cur_force, at_index + 1, basis):
            yield f
        for d in DIRS:
            next_force = cur_force + [(at_index, d)]
            if is_binary_force(patt, next_force, basis):
                yield next_force
            else:
                for f in force_backtrack(patt, next_force, at_index + 1, basis):
                    yield f

def generate_binary_forces_of_length(patt, length, basis=[]):
    """Yields forces of given length on the classical pattern such that the
    pattern is binary with respect to the force and the basis."""
    for points in permutations(range(len(patt)), length):
        for dirs in product(DIRS, repeat=length):
            force = list(zip(points, dirs))
            if is_binary_force(patt, force, basis):
                yield force

def generate_binary_forces(patt, basis=[]):
    """Yields all forces on the classical pattern such that the pattern is
    binary with respect to the force and the basis."""
    for length in range(len(patt) + 1):
        for force in generate_binary_forces_of_length(patt, length, basis):
            yield force

def generate_minimal_binary_forces(patt, basis=[]):
    for f in force_backtrack(patt, [], 0, basis):
        yield f

