from random import shuffle

from tilings import GriddedPerm, Tiling
from tilings import strategies as strat
from tilings.strategies import BasicVerificationStrategy
from tilings.tilescope import TileScope, TileScopePack

from comb_spec_searcher import (
    AtomStrategy,
    CartesianProductStrategy,
    CombinatorialClass,
    CombinatorialObject,
    CombinatorialSpecificationSearcher,
    DisjointUnionStrategy,
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


def tester(basis1: str, basis2: str):
    specs = find_bijection_between(basis_to_searcher(basis1), basis_to_searcher(basis2))
    if specs is None:
        print("Not found")
        return
    spec1, spec2 = specs
    # spec1.show()
    # spec2.show()
    bi = Bijection.construct(spec1, spec2)
    bi.map(GriddedPerm((2, 0, 1), ((0, 0), (0, 0), (0, 0))))
    assert bi is not None
    for i in range(5):
        print(i, flush=True)
        assert {bi.map(gp) for gp in spec1.generate_objects_of_size(i)} == set(
            spec2.generate_objects_of_size(i)
        )
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
    basis1 = "231_321"
    basis2 = "132_312"
    tester(basis1, basis2)


def test7():
    bases = """0132_0213_0231_0312_0321_1032_1302_1320_2031_2301_3120
        0132_0213_0231_0312_0321_1032_1302_1320_2301_3021_3120
        0132_0213_0231_0312_0321_1302_1320_2031_2301_3021_3120
        0132_0213_0231_0312_1032_1302_1320_2031_2301_3021_3120
        0132_0213_0231_0321_1032_1302_1320_2031_2301_3021_3120
        0132_0231_0312_0321_1032_1302_1320_2031_2301_3021_3120
        0213_0231_0312_0321_1032_1302_1320_2031_2301_3021_3120"""
    bases = list(map(str.strip, bases.splitlines()))

    # poor man's uf
    uf = [{b} for b in bases]

    connection = {}

    while len(uf) > 1:
        print(f"{len(uf)} grps")
        a, b = uf.pop(), uf.pop()
        break_outer = False
        for basis1 in a:
            for basis2 in b:
                specs = find_bijection_between(
                    basis_to_searcher(basis1), basis_to_searcher(basis2)
                )
                if specs:
                    print("Connection made!")
                    connection[tuple(sorted((basis1, basis2)))] = specs
                    uf.append(a.union(b))
                    break_outer = True
                    spec1, spec2 = specs
                    break
            if break_outer:
                break
        else:
            uf.append(a)
            uf.append(b)
            shuffle(uf)
            print("No connection made")
    print("DONE!", flush=True)
    for i, ((b1, b2), (s1, s2)) in enumerate(connection.items()):
        print(f"Connection: {i}\n{b1}\n{b2}", flush=True)
        assert s1.are_isomorphic(s2)
    print("Passed!")


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

    def atom_cmp_rev(a1: Tiling, a2: AvoidingWithPrefix) -> bool:
        if a2.prefix == "":
            return a1 == Tiling()
        if a2.prefix in ("a", "b"):
            return a1 == Tiling(
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
    # spec1.show()
    # spec2.show()

    bijection = Bijection.construct(spec2, spec1, atom_cmp)

    for i in range(7):
        assert set(bijection.map(w) for w in spec2.generate_objects_of_size(i)) == set(
            spec1.generate_objects_of_size(i)
        )

    for i in range(7):
        gps = list(spec1.generate_objects_of_size(i))
        assert set(bijection.inverse_map(gp) for gp in gps) == set(
            spec2.generate_objects_of_size(i)
        )

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
    bijection = spec2.get_bijection_to(spec1, atom_cmp)
    assert bijection is not None

    for i in range(10):
        words = list(spec2.generate_objects_of_size(i))
        assert set(bijection.map(w) for w in words) == set(
            spec1.generate_objects_of_size(i)
        )
    print("Passed")
    spec1.show()
    spec2.show()

    def map2perm(gp: GriddedPerm):
        if len(gp) == 0:
            return gp.patt.insert()
        if (1, 0) in gp._cells:
            return gp.patt.insert(len(gp) - 1)
        return gp.patt.insert(len(gp))

    for i in range(5):
        for w in sorted(list(spec2.generate_objects_of_size(i))):
            gp = bijection.map(w)
            print(f"{w} -> {gp} -> {map2perm(gp)}")


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
    bi = Bijection.construct(spec1, spec2)
    for i in range(5):
        assert {bi.map(gp) for gp in spec1.generate_objects_of_size(i)} == set(
            spec2.generate_objects_of_size(i)
        )
    print("Passed")


def test11():
    """tester(
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
    )"""
    tester(
        "0132_0213_0231_0312_0321_1032_1302_1320_2031_2301_3120",
        "0213_0231_0312_0321_1032_1302_1320_2031_2301_3021_3120",
    )


def main():
    # test1()
    # test2()
    # test3()
    # test4()
    # test5()
    # test6()
    # test7()
    # test8()
    # test9()
    # test10()
    test11()


if __name__ == "__main__":
    main()
