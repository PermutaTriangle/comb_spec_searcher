import json
from typing import Optional

from comb_spec_searcher import (
    AtomStrategy,
    CombinatorialSpecificationSearcher,
    StrategyPack,
)
from comb_spec_searcher.bijection import ParallelSpecFinder
from comb_spec_searcher.isomorphism import Bijection
from example import AvoidingWithPrefix, ExpansionStrategy, RemoveFrontOfPrefix, Word


def find_bijection_between(
    searcher1: CombinatorialSpecificationSearcher[AvoidingWithPrefix],
    searcher2: CombinatorialSpecificationSearcher[AvoidingWithPrefix],
) -> Optional[Bijection]:
    specs = ParallelSpecFinder[AvoidingWithPrefix, Word, AvoidingWithPrefix, Word](
        searcher1, searcher2
    ).find()
    if specs is not None:
        s1, s2 = specs
        return Bijection.construct(s1, s2)


def get_word_searcher(avoid, alphabet):
    pack = StrategyPack(
        initial_strats=[RemoveFrontOfPrefix()],
        inferral_strats=[],
        expansion_strats=[[ExpansionStrategy()]],
        ver_strats=[AtomStrategy()],
        name=("Finding specification for words avoiding consecutive patterns."),
    )
    start_class = AvoidingWithPrefix("", avoid, alphabet)
    searcher = CombinatorialSpecificationSearcher(start_class, pack)
    return searcher


def get_bijection(alphabet1, avoid1, alphabet2, avoid2):
    s1, s2 = get_word_searcher(avoid1, alphabet1), get_word_searcher(avoid2, alphabet2)
    return find_bijection_between(s1, s2)


def assert_mappings(bijection):
    assert bijection is not None
    assert all(
        set(bijection.map(w) for w in bijection.domain.generate_objects_of_size(i))
        == set(bijection.codomain.generate_objects_of_size(i))
        and set(
            bijection.inverse_map(w)
            for w in bijection.codomain.generate_objects_of_size(i)
        )
        == set(bijection.domain.generate_objects_of_size(i))
        and all(
            w == bijection.inverse_map(bijection.map(w))
            for w in bijection.domain.generate_objects_of_size(i)
        )
        for i in range(10)
    )


def test_finding_bijection_and_map_in_words():
    bijection = get_bijection(["0", "1"], ["00"], ["0", "1"], ["11"])
    assert bijection is not None
    assert_mappings(bijection)


def test_finding_bijection_and_map_in_words2():
    bijection = get_bijection(["a", "b"], ["aa"], ["0", "1"], ["11"])
    assert bijection is not None
    assert_mappings(bijection)


def test_finding_bijection_and_map_in_words3():
    bijection = get_bijection(["0", "1"], ["1011", "101"], ["0", "1"], ["010", "0101"])
    assert bijection is not None
    assert_mappings(bijection)


def test_non_equal_classes():
    bijection = get_bijection(["0", "1"], ["00"], ["0", "1"], ["101"])
    assert bijection is None


def test_constructing_bijection_non_eq_classes():
    assert (
        Bijection.construct(
            get_word_searcher(["00"], ["0", "1"]).auto_search(),
            get_word_searcher(["101"], ["0", "1"]).auto_search(),
        )
        is None
    )


def test_bijection_jsonable():
    bijection = get_bijection(["0", "1"], ["1011", "101"], ["0", "1"], ["010", "0101"])
    assert bijection is not None
    assert_mappings(
        Bijection.from_dict(json.loads(json.dumps(bijection.to_jsonable())))
    )
