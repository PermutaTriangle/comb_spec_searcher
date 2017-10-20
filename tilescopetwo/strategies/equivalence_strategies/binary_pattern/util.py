from permuta import PermSet, Perm
from permuta.misc import DIRS, DIR_EAST, DIR_WEST, DIR_SOUTH  # DIR_NORTH,
from itertools import chain, permutations, product


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


def task_to_basis(task):
    return [Perm.to_standard(map(int, t)) for t in task.split("_")]


def make_force_strength_func(force):
    def keyfunc(occ, perm):
        return [
            -occ[i] if d == DIR_WEST else
            occ[i] if d == DIR_EAST else
            -perm[occ[i]] if d == DIR_SOUTH else
            perm[occ[i]] for (i, d) in force]
    return keyfunc


def is_binary_force(patt, force, basis=[]):
    """Given a classical pattern patt and a force, checks if the pattern is
    binary with respect to the force and the basis."""
    permset = PermSet.avoiding(basis)
    perms = chain.from_iterable(
        permset.of_length(i)
        for i in range(len(force), 2*len(patt) - len(force) + 1))
    force_strength = make_force_strength_func(force)
    for p in perms:
        forced = [force_strength(occ, p) for occ in patt.occurrences_in(p)]
        if len(forced) > 0:
            if forced.count(max(forced)) > 1:
                return False
    return True


def force_backtrack(patt, cur_force, index, basis, maxlen):
    if len(cur_force) == maxlen:
        return
    if index < len(patt):
        for f in force_backtrack(patt, cur_force, index + 1, basis, maxlen):
            yield f
        for d in DIRS:
            next_force = cur_force + [(index, d)]
            if is_binary_force(patt, next_force, basis):
                yield next_force
            else:
                for f in force_backtrack(patt, next_force, index + 1,
                                         basis, maxlen):
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


def generate_minimal_binary_forces(patt, basis=[], maxlen=None):
    if is_binary_force(patt, [], basis):
        yield tuple()
        return
    if maxlen is None:
        maxlen = len(patt)
    for f in force_backtrack(patt, [], 0, basis, maxlen):
        yield f
