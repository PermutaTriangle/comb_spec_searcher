from random import shuffle

from comb_spec_searcher.bijection import ParallelSpecFinder
from comb_spec_searcher.comb_spec_searcher import CombinatorialSpecificationSearcher

try:
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
    psf = ParallelSpecFinder(basis_to_searcher(basis1), basis_to_searcher(basis2))
    specs = psf.find()
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
    psf = ParallelSpecFinder(basis_to_searcher(basis1), basis_to_searcher(basis2))
    assert psf.find() is None
    print("Passed")


def test4():
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
                psf = ParallelSpecFinder(
                    basis_to_searcher(basis1), basis_to_searcher(basis2)
                )
                specs = psf.find()
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


if __name__ == "__main__":
    test1(plot=False)
    test2(plot=False)
    test3()
    test4()  # This can take some time...
