import json

from comb_spec_searcher import (
    AtomStrategy,
    CombinatorialClass,
    CombinatorialSpecificationSearcher,
    StrategyPack,
)
from comb_spec_searcher.bijection import find_bijection_between
from comb_spec_searcher.isomorphism import Bijection
from example import AvoidingWithPrefix, ExpansionStrategy, RemoveFrontOfPrefix


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


def atom_cmp(atom1: CombinatorialClass, atom2: CombinatorialClass) -> bool:
    assert isinstance(atom1, AvoidingWithPrefix)
    assert isinstance(atom2, AvoidingWithPrefix)
    return len(atom1.prefix) == len(atom2.prefix)


def get_specs(alphabet1, avoid1, alphabet2, avoid2):
    s1, s2 = get_word_searcher(avoid1, alphabet1), get_word_searcher(avoid2, alphabet2)
    return find_bijection_between(s1, s2, atom_cmp)


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
    specs = get_specs(["0", "1"], ["00"], ["0", "1"], ["11"])
    assert specs is not None
    assert_mappings(Bijection.construct(*specs, atom_cmp))


def test_finding_bijection_and_map_in_words2():
    specs = get_specs(["a", "b"], ["aa"], ["0", "1"], ["11"])
    assert specs is not None
    assert_mappings(Bijection.construct(*specs, atom_cmp))


def test_finding_bijection_and_map_in_words3():
    specs = get_specs(["0", "1"], ["1011", "101"], ["0", "1"], ["010", "0101"])
    assert specs is not None
    assert_mappings(Bijection.construct(*specs, atom_cmp))


def test_non_equal_classes():
    specs = get_specs(["0", "1"], ["00"], ["0", "1"], ["101"])
    assert specs is None


def test_constructing_bijection_non_eq_classes():
    assert (
        Bijection.construct(
            get_word_searcher(["00"], ["0", "1"]).auto_search(),
            get_word_searcher(["101"], ["0", "1"]).auto_search(),
            atom_cmp,
        )
        is None
    )


def test_bijection_jsonable():
    specs = get_specs(["0", "1"], ["1011", "101"], ["0", "1"], ["010", "0101"])
    assert specs is not None
    assert_mappings(
        Bijection.from_dict(
            json.loads(json.dumps(Bijection.construct(*specs, atom_cmp).to_jsonable()))
        )
    )
