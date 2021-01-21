from random import shuffle

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
from example import AvoidingWithPrefix, ExpansionStrategy, RemoveFrontOfPrefix

try:
    from tilings import GriddedPerm, Tiling
    from tilings.strategies import BasicVerificationStrategy
    from tilings.tilescope import TileScope, TileScopePack
except ImportError:
    pass


def basis_to_searcher(basis: str) -> CombinatorialSpecificationSearcher:
    pack = TileScopePack.row_and_col_placements(row_only=True)
    pack = pack.add_verification(BasicVerificationStrategy(), replace=True)
    searcher = TileScope(basis, pack)
    assert isinstance(searcher, CombinatorialSpecificationSearcher)
    return searcher


def tester(basis1: str, basis2: str, plot: bool):
    specs = find_bijection_between(basis_to_searcher(basis1), basis_to_searcher(basis2))
    if specs is None:
        print("Not found")
        return
    spec1, spec2 = specs
    assert spec1.are_isomorphic(spec2)
    if plot:
        spec1.show()
        spec2.show()
    print("Passed")


def test1(plot: bool = False):
    basis1 = "132"
    basis2 = "231"
    tester(basis1, basis2, plot)


def test2(plot: bool = False):
    basis1 = "0132_0213_0231_0312_1032_1302_1320_2031_2301_3021_3120"
    basis2 = "0132_0213_0231_0312_0321_1302_1320_2031_2301_3021_3120"
    tester(basis1, basis2, plot)


def test3():
    # Not equal
    basis1 = "0132_0213_0231_0312_1032_1302_1320_2031_2301_3021_3120"
    basis2 = "0132_0213_0231_0312_0321_1230_1320_2031_2301_3021_3120"
    specs = find_bijection_between(basis_to_searcher(basis1), basis_to_searcher(basis2))
    assert specs is None
    print("Passed")


def test4(plot: bool = False):
    basis1 = "231_321"
    basis2 = "132_312"
    tester(basis1, basis2, plot)


def test5():
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
        print(f"Connection: {i}\n{b1}\n{b2}")
        assert s1.are_isomorphic(s2)
    print("Passed!")


def test6(plot: bool = False):
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

    if plot:
        spec1.show()
        spec2.show()

    bijection = spec2.get_bijection_to(spec1, atom_cmp)
    bijection2 = spec1.get_bijection_to(spec2, atom_cmp_rev)

    for i in range(10):
        words = list(spec2.generate_objects_of_size(i))
        assert set(bijection.map(w) for w in words) == set(
            spec1.generate_objects_of_size(i)
        )

    for i in range(10):
        gps = list(spec1.generate_objects_of_size(i))
        assert set(bijection2.map(gp) for gp in gps) == set(
            spec2.generate_objects_of_size(i)
        )

    print("passed")


def main():
    # test1(plot=False)
    # test2(plot=False)
    # test3()
    # test4(plot=False)
    # test5()  # This can take some time...
    test6()


if __name__ == "__main__":
    main()
