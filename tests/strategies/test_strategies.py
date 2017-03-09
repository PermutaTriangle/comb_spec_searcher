import atrap
import pytest

from grids import Tiling

from fixtures import external_strategy
from fixtures import internal_strategy
from fixtures import random_basis
from fixtures import random_tiling_dict


def test_internal_strategies(internal_strategy,
                             random_tiling_dict,
                             random_basis):
    """TODO""" #  TODO doc
    tiling = Tiling(random_tiling_dict)
    basis = random_basis

    print("Applying internal strategy to tiling:")
    print()
    print(tiling)
    print()
    print("While working in basis:")
    print(basis)

    # Some arbitrary length to verify to
    verification_length = tiling.total_points + len(basis[-1]) + 2

    # Construct the actual set of perms in the tiling
    actual_perms = {}
    #map(actual_perms.update, for length in range(verification_length + 1)))
    for length in range(verification_length + 1):
        actual_perms[length] = set(perm for perm
                                   in tiling.perms_of_length(length) \
                                   if perm.avoids(*basis))

    for _, strategy_tiling in internal_strategy(tiling, basis=basis):
        print()
        print("Looking at strategy tiling:")
        print()
        print(strategy_tiling)
        print()
        for length in range(verification_length + 1):
            strategy_perms = set()
            for perm in strategy_tiling.perms_of_length(length):
                if perm.avoids(*basis):
                    strategy_perms.add(perm)
            assert strategy_perms == actual_perms[length]
            print("OK for length", length)
        print()
        print("Strategy tiling passed test")


#    separated_tiling = row_and_column_separations(tiling, basis)
#
#    verification_length = tiling.total_points + len(basis[-1])
#
#    for length in range(verification_length + 1):
#        actual_perms = set()
#        for perm in tiling.perms_of_length(length):
#            if perm.avoids(*basis):
#                actual_perms.add(perm)
#
#        separated_perms = set()
#        for perm in tiling.perms_of_length(length):
#            if perm.avoids(*basis):
#                separated_perms.add(perm)
#
#        assert actual_perms == separated_perms
