"""A strategy for checking if a tiling is a subset of the class."""

from comb_spec_searcher import VerificationStrategy
from grids_two import Tiling, Obstruction
from permuta import Perm

database = {
    Tiling(possibly_empty=[(0, 0), (0, 1)],
           obstructions=[Obstruction(Perm((0, 1)),
                                     [(0, 0), (0, 0)]),
                         Obstruction(Perm((0, 1, 2)),
                                     [(0, 0), (0, 1), (0, 1)]),
                         Obstruction(Perm((0, 1, 2)),
                                     [(0, 1), (0, 1), (0, 1)])]),
    Tiling(possibly_empty=[(0, 0), (0, 1)],
           obstructions=[Obstruction(Perm((0, 1)),
                                     [(0, 1), (0, 1)]),
                         Obstruction(Perm((0, 1, 2)),
                                     [(0, 0), (0, 0), (0, 1)]),
                         Obstruction(Perm((0, 1, 2)),
                                     [(0, 0), (0, 0), (0, 0)])]),
    Tiling(possibly_empty=[(0, 0), (1, 0)],
           obstructions=[Obstruction(Perm((0, 1)),
                                     [(1, 0), (1, 0)]),
                         Obstruction(Perm((0, 1, 2)),
                                     [(0, 0), (0, 0), (1, 0)]),
                         Obstruction(Perm((0, 1, 2)),
                                     [(0, 0), (0, 0), (0, 0)])]),
    Tiling(possibly_empty=[(0, 0), (1, 0)],
           obstructions=[Obstruction(Perm((0, 1)), [(0, 0), (0, 0)]),
                         Obstruction(Perm((0, 1, 2)),
                                     [(0, 0), (1, 0), (1, 0)]),
                         Obstruction(Perm((0, 1, 2)),
                                     [(1, 0), (1, 0), (1, 0)])])
    Tiling(possibly_empty=[(0, 0), (0, 1), (1, 1)],
           obstructions=[Obstruction(Perm((0, 1)), [(0, 0), (0, 0)]),
                         Obstruction(Perm((0, 1)), [(1, 1), (1, 1)]),
                         Obstruction(Perm((0, 1, 2)), [(0, 0), (0, 1), (1, 1)]),
                         Obstruction(Perm((0, 1, 2)), [(0, 0), (0, 1), (0, 1)]),
                         Obstruction(Perm((0, 1, 2)), [(0, 1), (0, 1), (1, 1)]),
                         Obstruction(Perm((0, 1, 2)), [(0, 1), (0, 1), (0, 1)])])
    Tiling(possibly_empty=[(0, 1), (1, 0), (1, 1)],
           obstructions=[Obstruction(Perm((1, 0)), ((0, 1), (0, 1))),
                         Obstruction(Perm((1, 0)), ((1, 0), (1, 0))),
                         Obstruction(Perm((2, 1, 0)), ((0, 1), (1, 1), (1, 0))),
                         Obstruction(Perm((2, 1, 0)), ((0, 1), (1, 1), (1, 1))),
                         Obstruction(Perm((2, 1, 0)), ((1, 1), (1, 1), (1, 0))),
                         Obstruction(Perm((2, 1, 0)), ((1, 1), (1, 1), (1, 1)))])
    Tiling(possibly_empty=[(1, 0), (0, 0), (1, 1)],
           obstructions=[Obstruction(Perm((0, 1)), ((0, 0), (0, 0))),
                         Obstruction(Perm((0, 1)), ((1, 1), (1, 1))),
                         Obstruction(Perm((0, 1, 2)), ((0, 0), (1, 0), (1, 0))),
                         Obstruction(Perm((0, 1, 2)), ((0, 0), (1, 0), (1, 1))),
                         Obstruction(Perm((0, 1, 2)), ((1, 0), (1, 0), (1, 0))),
                         Obstruction(Perm((0, 1, 2)), ((1, 0), (1, 0), (1, 1)))])
    Tiling(possibly_empty=[(0, 1), (1, 0), (0, 0)],
           obstructions=[Obstruction(Perm((1, 0)), ((0, 1), (0, 1))),
                         Obstruction(Perm((1, 0)), ((1, 0), (1, 0))),
                         Obstruction(Perm((2, 1, 0)), ((0, 0), (0, 0), (0, 0))),
                         Obstruction(Perm((2, 1, 0)), ((0, 0), (0, 0), (1, 0))),
                         Obstruction(Perm((2, 1, 0)), ((0, 1), (0, 0), (0, 0))),
                         Obstruction(Perm((2, 1, 0)), ((0, 1), (0, 0), (1, 0)))])
                                     }


def database_verified(tiling, **kwargs):
    if tiling in database:
        yield VerificationStrategy("Already in database!")
