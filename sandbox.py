from random import shuffle

from tilings import GriddedPerm, Tiling
from tilings import strategies as strat
from tilings.strategies import BasicVerificationStrategy
from tilings.tilescope import TileScope, TileScopePack

from comb_spec_searcher import (
    AtomStrategy,
    CombinatorialSpecificationSearcher,
    StrategyPack,
)
from comb_spec_searcher.bijection import find_bijection_between
from comb_spec_searcher.isomorphism import Bijection
from example import AvoidingWithPrefix, ExpansionStrategy, RemoveFrontOfPrefix


def basis_to_searcher(basis: str) -> CombinatorialSpecificationSearcher:
    pack = TileScopePack.row_and_col_placements(row_only=True)
    pack = pack.add_verification(BasicVerificationStrategy(), replace=True)
    searcher = TileScope(basis, pack)
    assert isinstance(searcher, CombinatorialSpecificationSearcher)
    return searcher


def bijection_asserter(spec1, spec2, atom_cmp=None):
    bi = (
        Bijection.construct(spec1, spec2)
        if atom_cmp is None
        else Bijection.construct(spec1, spec2, atom_cmp)
    )
    assert bi is not None
    for i in range(10):
        assert {bi.map(gp) for gp in spec1.generate_objects_of_size(i)} == set(
            spec2.generate_objects_of_size(i)
        )
        assert {bi.inverse_map(gp) for gp in spec2.generate_objects_of_size(i)} == set(
            spec1.generate_objects_of_size(i)
        )
        for gp in spec1.generate_objects_of_size(i):
            assert bi.inverse_map(bi.map(gp)) == gp


def tester(basis1: str, basis2: str):
    specs = find_bijection_between(basis_to_searcher(basis1), basis_to_searcher(basis2))
    assert specs is not None
    spec1, spec2 = specs
    bijection_asserter(spec1, spec2)
    print("Passed")


def test1():
    tester(
        "0132_0213_0231_0312_1302_1320_2031_2301_3021_3120",
        "0132_0213_0231_0321_1302_1320_2031_2301_3021_3120",
    )


def test2():
    tester(
        "0132_0213_0231_0312_0321_1032_1320_2301_3021_3120",
        "0132_0213_0231_0312_1032_1302_1320_2301_3021_3120",
    )


def test3():
    tester("132", "231")


def test4():
    basis1 = "0132_0213_0231_0312_1032_1302_1320_2031_2301_3021_3120"
    basis2 = "0132_0213_0231_0312_0321_1302_1320_2031_2301_3021_3120"
    tester(basis1, basis2)


def test5():
    basis1 = "0132_0213_0231_0312_1032_1302_1320_2031_2301_3021_3120"
    basis2 = "0132_0213_0231_0312_0321_1230_1320_2031_2301_3021_3120"
    specs = find_bijection_between(basis_to_searcher(basis1), basis_to_searcher(basis2))
    assert specs is None
    print("Passed")


def test6():
    tester("231_312", "231_321")
    tester("231_321", "132_312")


def test7():
    tester(
        "0132_0231_0312_0321_1032_1302_1320_2031_2301_3021_3120",
        "0213_0231_0312_0321_1032_1302_1320_2031_2301_3021_3120",
    )
    tester(
        "0132_0213_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        "0132_0231_0312_0321_1032_1302_1320_2031_2301_3021_3120",
    )
    tester(
        "0132_0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        "0132_0231_0312_0321_1032_1302_1320_2031_2301_3021_3120",
    )
    tester(
        "0132_0213_0231_0312_0321_1302_1320_2031_2301_3021_3120",
        "0132_0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
    )
    tester(
        "0132_0213_0231_0312_0321_1032_1302_1320_2301_3021_3120",
        "0213_0231_0312_0321_1032_1302_1320_2031_2301_3021_3120",
    )
    tester(
        "0132_0213_0231_0312_0321_1032_1302_1320_2031_2301_3120",
        "0213_0231_0312_0321_1032_1302_1320_2031_2301_3021_3120",
    )


def test8():
    # 231_321 after row placement and factoring
    t = Tiling(
        obstructions=(
            GriddedPerm((1, 0), ((0, 0), (1, 0))),
            GriddedPerm((1, 0), ((1, 0), (1, 0))),
            GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((2, 1, 0), ((0, 0), (0, 0), (0, 0))),
        ),
        requirements=(),
        assumptions=(),
    )
    pack = TileScopePack.row_and_col_placements(row_only=True)
    pack = pack.add_verification(BasicVerificationStrategy(), replace=True)
    pack.inferral_strats = ()
    searcher1 = TileScope(t, pack)

    pack = StrategyPack(
        initial_strats=[RemoveFrontOfPrefix()],
        inferral_strats=[],
        expansion_strats=[[ExpansionStrategy()]],
        ver_strats=[AtomStrategy()],
        name=("Finding specification for words avoiding consecutive patterns."),
    )
    start_class = AvoidingWithPrefix("", [], ["a", "b"])
    searcher2 = CombinatorialSpecificationSearcher(start_class, pack)

    def atom_cmp(a1: AvoidingWithPrefix, a2: Tiling) -> bool:
        if a1.prefix == "":
            return a2 == Tiling()
        if a1.prefix in ("a", "b"):
            return a2 == Tiling(
                obstructions=(
                    GriddedPerm((0, 1), ((0, 0), (0, 0))),
                    GriddedPerm((1, 0), ((0, 0), (0, 0))),
                ),
                requirements=((GriddedPerm((0,), ((0, 0),)),),),
            )
        return False

    specs = find_bijection_between(searcher2, searcher1, atom_cmp)
    if specs is None:
        print("Nothing found")
        return
    spec2, spec1 = specs
    bijection_asserter(spec2, spec1, atom_cmp)
    print("passed")


def test9():
    # 231_312_321 after a single row placement + factoring
    t = Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
            GriddedPerm((1, 0), ((0, 0), (1, 0))),
            GriddedPerm((1, 0), ((1, 0), (1, 0))),
            GriddedPerm((1, 2, 0), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((2, 0, 1), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((2, 1, 0), ((0, 0), (0, 0), (0, 0))),
        ),
        requirements=(),
        assumptions=(),
    )
    pack = TileScopePack(
        initial_strats=[
            strat.FactorFactory(unions=True, workable=False, ignore_parent=False),
        ],
        ver_strats=[
            strat.BasicVerificationStrategy(),
            # strat.OneByOneVerificationStrategy(), # gives left spec
        ],
        inferral_strats=[],
        expansion_strats=[
            [
                strat.RowAndColumnPlacementFactory(
                    place_row=True, place_col=False, partial=False
                ),
            ],
        ],
        name=".............",
    )
    searcher1 = TileScope(t, pack)
    pack = StrategyPack(
        initial_strats=[RemoveFrontOfPrefix()],
        inferral_strats=[],
        expansion_strats=[[ExpansionStrategy()]],
        ver_strats=[AtomStrategy()],
        name=("Finding specification for words avoiding consecutive patterns."),
    )
    start_class = AvoidingWithPrefix("", ["bb"], ["a", "b"])
    searcher2 = CombinatorialSpecificationSearcher(start_class, pack)

    def atom_cmp(a1: AvoidingWithPrefix, a2: Tiling) -> bool:
        if a1.prefix == "":
            return a2 == Tiling()
        if a1.prefix in ("a", "b"):
            return a2 == Tiling(
                obstructions=(
                    GriddedPerm((0, 1), ((0, 0), (0, 0))),
                    GriddedPerm((1, 0), ((0, 0), (0, 0))),
                ),
                requirements=((GriddedPerm((0,), ((0, 0),)),),),
            )
        if a1.prefix == "ba":
            return a2 == Tiling(
                obstructions=(
                    GriddedPerm((0, 1), ((0, 0), (0, 0))),
                    GriddedPerm((0, 1), ((1, 1), (1, 1))),
                    GriddedPerm((1, 0), ((0, 0), (0, 0))),
                    GriddedPerm((1, 0), ((1, 1), (1, 1))),
                ),
                requirements=(
                    (GriddedPerm((0,), ((0, 0),)),),
                    (GriddedPerm((0,), ((1, 1),)),),
                ),
                assumptions=(),
            )
        return False

    specs = find_bijection_between(searcher2, searcher1, atom_cmp)
    if specs is None:
        print("Nothing found")
        return
    spec2, spec1 = specs
    bijection_asserter(spec2, spec1, atom_cmp)
    print("Passed")


def test10():
    pack1 = TileScopePack.requirement_placements()
    pack1 = pack1.add_verification(BasicVerificationStrategy(), replace=True)
    searcher1 = TileScope("132_4312", pack1)
    pack2 = TileScopePack.requirement_placements()
    pack2 = pack2.add_verification(BasicVerificationStrategy(), replace=True)
    searcher2 = TileScope("132_4231", pack2)
    specs = find_bijection_between(searcher1, searcher2)
    if specs is None:
        print("Not found")
        return
    spec1, spec2 = specs
    bijection_asserter(spec1, spec2)
    print("Passed")


def test11():
    pairs = [
        (
            "0132_0213_0231_0312_0321_1302_1320_2031_2301_3120",
            "0132_0213_0231_0321_1032_1302_1320_2031_2301_3120",
        ),
        (
            "0132_0213_0231_0312_0321_1302_1320_2031_2301_3120",
            "0213_0231_0312_0321_1032_1302_1320_2031_2301_3120",
        ),
        (
            "0132_0213_0231_0312_0321_1302_1320_2301_3021_3120",
            "0213_0231_0312_0321_1032_1302_1320_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0312_1032_1302_1320_2031_2301_3120",
            "0132_0213_0231_0321_1032_1302_1320_2031_2301_3120",
        ),
        (
            "0132_0213_0231_0312_1032_1302_1320_2031_2301_3120",
            "0132_0213_0231_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0312_1032_1302_1320_2031_2301_3120",
            "0132_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0312_1032_1302_1320_2031_2301_3120",
            "0213_0231_0312_0321_1032_1302_1320_2031_2301_3120",
        ),
        (
            "0132_0213_0231_0312_1032_1302_1320_2031_2301_3120",
            "0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0312_1302_1320_2031_2301_3021_3120",
            "0132_0213_0231_0321_1032_1302_1320_2031_2301_3120",
        ),
        (
            "0132_0213_0231_0312_1302_1320_2031_2301_3021_3120",
            "0132_0213_0231_0321_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0312_1302_1320_2031_2301_3021_3120",
            "0132_0213_0231_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0312_1302_1320_2031_2301_3021_3120",
            "0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0312_1302_1320_2031_2301_3021_3120",
            "0213_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0321_1032_1302_1320_2031_2301_3120",
            "0132_0213_0231_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0321_1032_1302_1320_2031_2301_3120",
            "0132_0231_0312_0321_1032_1302_1320_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0321_1032_1302_1320_2031_2301_3120",
            "0132_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0321_1032_1302_1320_2031_2301_3120",
            "0213_0231_0312_0321_1032_1302_1320_2031_2301_3120",
        ),
        (
            "0132_0213_0231_0321_1032_1302_1320_2031_2301_3120",
            "0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0321_1302_1320_2031_2301_3021_3120",
            "0132_0213_0231_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0321_1302_1320_2031_2301_3021_3120",
            "0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_0321_1302_1320_2031_2301_3021_3120",
            "0213_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_1032_1302_1320_2031_2301_3021_3120",
            "0132_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_1032_1302_1320_2031_2301_3021_3120",
            "0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0213_0231_1032_1302_1320_2031_2301_3021_3120",
            "0213_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0231_0312_0321_1032_1302_1320_2301_3021_3120",
            "0132_0231_0312_0321_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0231_0312_0321_1032_1302_1320_2301_3021_3120",
            "0132_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0231_0312_0321_1032_1302_1320_2301_3021_3120",
            "0132_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0231_0312_0321_1032_1302_1320_2301_3021_3120",
            "0213_0231_1032_1203_1230_1302_1320_2031_2130_2301",
        ),
        (
            "0132_0231_0312_0321_1302_1320_2031_2301_3021_3120",
            "0132_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0231_0312_0321_1302_1320_2031_2301_3021_3120",
            "0132_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0231_0312_0321_1302_1320_2031_2301_3021_3120",
            "0213_0231_1032_1203_1230_1302_1320_2031_2130_2301",
        ),
        (
            "0132_0231_0312_1032_1302_1320_2031_2301_3021_3120",
            "0132_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0231_0312_1032_1302_1320_2031_2301_3021_3120",
            "0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0231_0312_1032_1302_1320_2031_2301_3021_3120",
            "0213_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0231_0312_1032_1302_1320_2031_2301_3021_3120",
            "0213_0231_1032_1203_1230_1302_1320_2031_2130_2301",
        ),
        (
            "0132_0231_0321_1032_1302_1320_2031_2301_3021_3120",
            "0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0231_0321_1032_1302_1320_2031_2301_3021_3120",
            "0213_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0132_0231_0321_1032_1302_1320_2031_2301_3021_3120",
            "0213_0231_1032_1203_1230_1302_1320_2031_2130_2301",
        ),
        (
            "0213_0231_0312_0321_1032_1302_1320_2031_2301_3120",
            "0213_0231_0312_0321_1032_1302_1320_2301_3021_3120",
        ),
        (
            "0213_0231_0312_0321_1032_1302_1320_2031_2301_3120",
            "0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0213_0231_0312_0321_1032_1302_1320_2031_2301_3120",
            "0213_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0213_0231_0312_0321_1032_1302_1320_2031_2301_3120",
            "0213_0231_1032_1203_1230_1302_1320_2031_2130_2301",
        ),
        (
            "0213_0231_0312_0321_1032_1302_1320_2301_3021_3120",
            "0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0213_0231_0312_0321_1032_1302_1320_2301_3021_3120",
            "0213_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0213_0231_0312_0321_1032_1302_1320_2301_3021_3120",
            "0213_0231_1032_1203_1230_1302_1320_2031_2130_2301",
        ),
        (
            "0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
            "0213_0231_0321_1032_1302_1320_2031_2301_3021_3120",
        ),
        (
            "0213_0231_0312_1032_1302_1320_2031_2301_3021_3120",
            "0213_0231_1032_1203_1230_1302_1320_2031_2130_2301",
        ),
        (
            "0213_0231_0321_1032_1302_1320_2031_2301_3021_3120",
            "0213_0231_1032_1203_1230_1302_1320_2031_2130_2301",
        ),
    ]
    shuffle(pairs)
    for basis1, basis2 in pairs[:5]:
        tester(basis1, basis2)


def test12():
    bases = [
        "321_2341",
        "321_3412",  # pnt rowcol needed
        "321_3142",  # pnt rowcol needed
        "132_1234",
        "132_4213",
        "132_4123",
        "132_3124",
        "132_2134",
        "132_3412",  # pnt rowcol needed
    ]

    def pntrcpls(b1, b2):
        pack = TileScopePack.point_and_row_and_col_placements(row_only=True)
        pack = pack.add_verification(BasicVerificationStrategy(), replace=True)
        searcher1 = TileScope("321_3412", pack)
        searcher2 = TileScope("132_4123", pack)
        return find_bijection_between(searcher1, searcher2)

    # bijection_asserter(*pntrcpls("132_1234", "132_3412")) # forward map bug
    # bijection_asserter(*pntrcpls("321_3412", "321_3142")) # forward map bug
    # bijection_asserter(*pntrcpls("321_3412", "132_3412")) # forward map bug
    tester(bases[0], bases[4])
    tester(bases[3], bases[4])
    tester(bases[3], bases[5])
    tester(bases[3], bases[6])
    tester(bases[3], bases[7])


def test13():
    pack = TileScopePack.point_and_row_and_col_placements(row_only=True)
    pack = pack.add_verification(BasicVerificationStrategy(), replace=True)
    searcher1 = TileScope("0132_0213_0231_0321_1032_1320_2031_2301_3021_3120", pack)
    searcher2 = TileScope("0132_0213_0231_0312_0321_1302_1320_2031_2301_3120", pack)
    specs = find_bijection_between(searcher1, searcher2)
    assert specs is not None
    # bijection_asserter(*specs) # forward map bug


def main():
    test1()
    test2()
    test3()
    test4()
    test5()
    test6()
    test7()
    test8()
    test9()
    test10()
    test11()
    test12()
    test13()
    pass


if __name__ == "__main__":
    main()
