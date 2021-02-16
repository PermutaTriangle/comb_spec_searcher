from collections import defaultdict, deque
from itertools import product
from typing import Callable, DefaultDict, Dict, List, Optional, Set, Tuple

from comb_spec_searcher.comb_spec_searcher import CombinatorialSpecificationSearcher
from comb_spec_searcher.combinatorial_class import CombinatorialClass
from comb_spec_searcher.exception import NoMoreClassesToExpandError
from comb_spec_searcher.rule_db.base import RuleDBBase
from comb_spec_searcher.specification import CombinatorialSpecification
from comb_spec_searcher.specification_extrator import SpecificationRuleExtractor
from comb_spec_searcher.strategies.rule import Rule
from comb_spec_searcher.tree_searcher import Node, prune
from comb_spec_searcher.typing import RuleKey

NO_CONSTRUCTOR = None.__class__
MATCHING_INFO = Dict[Tuple[int, int], Set[Tuple[Tuple[int, ...], Tuple[int, ...]]]]


class ParallelInfo:
    """Information from searcher essential to finding bijection with another and then
    to create specifications.
    """

    def __init__(self, searcher: CombinatorialSpecificationSearcher):
        self.searcher: CombinatorialSpecificationSearcher = searcher
        self._expand()
        self.r_db: RuleDBBase = self.searcher.ruledb
        self.rule_dict: Dict[
            int, Set[Tuple[int, ...]]
        ] = self.r_db.rules_up_to_equivalence()
        prune(self.rule_dict)
        self.root_label: int = self.searcher.start_label
        self.root_eq_label: int = self.r_db.equivdb[self.root_label]
        self.atom_map: Dict[int, CombinatorialClass] = {}
        self.root_class: Optional[CombinatorialClass] = None
        self.debug_map: Dict[
            Tuple[int, Tuple[int, ...]],
            Tuple[CombinatorialClass, Tuple[CombinatorialClass, ...]],
        ] = {}
        self.eq_label_rules: DefaultDict[
            int, DefaultDict[type, DefaultDict[int, Set[Tuple[int, ...]]]]
        ] = self._construct_eq_label_rules()

    def _expand(self):
        try:
            while self.searcher.get_specification(minimization_time_limit=0) is None:
                self.searcher.do_level()
        except NoMoreClassesToExpandError:
            assert (
                self.searcher.get_specification(minimization_time_limit=0) is not None
            )

    def _construct_eq_label_rules(
        self,
    ) -> DefaultDict[int, DefaultDict[type, DefaultDict[int, Set[Tuple[int, ...]]]]]:
        """
        Creates a dictionary d such that
            d[label][rule_type][number_of_children]
        is a set of possible resulting children ids (grouped into tuples of length
        number_of_children) by applying rule_type to label.
        """
        lis, rule_dict, eq_label_rules = self._construct_eq_labels_init()

        for eq_par, eq_chi in lis:
            actual_par, actual_children = rule_dict[(eq_par, eq_chi)]
            strategy = self.r_db.rule_to_strategy[(actual_par, actual_children)]
            parent = self.searcher.classdb.get_class(actual_par)
            children = tuple(map(self.searcher.classdb.get_class, actual_children))
            self.debug_map[(eq_par, eq_chi)] = (parent, children)
            rule = strategy(parent, children)
            if eq_par == self.root_eq_label and self.root_class is None:
                self.root_class = parent
            if parent.is_atom():
                eq_label_rules[eq_par][NO_CONSTRUCTOR][len(children)].add(eq_chi)
                self.atom_map[eq_par] = parent
            else:
                assert isinstance(rule, Rule)
                non_empty_children = tuple(
                    eq_chi[i] for i, c in enumerate(children) if not c.is_empty()
                )
                eq_label_rules[eq_par][rule.constructor.__class__][
                    len(non_empty_children)
                ].add(non_empty_children)
        return eq_label_rules

    def _construct_eq_labels_init(
        self,
    ) -> Tuple[
        List[Tuple[int, Tuple[int, ...]]],
        Dict[RuleKey, RuleKey],
        DefaultDict[int, DefaultDict[type, DefaultDict[int, Set[Tuple[int, ...]]]]],
    ]:
        lis = [(k, c) for k, v in self.rule_dict.items() for c in v]
        rule_dict = self.r_db.rule_from_equivalence_rule_dict(lis)
        eq_label_rules: DefaultDict[
            int, DefaultDict[type, DefaultDict[int, Set[Tuple[int, ...]]]]
        ] = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
        return lis, rule_dict, eq_label_rules


class ParallelSpecFinder:
    """Finder for paralell specs."""

    _INVALID, _UNKNOWN, _VALID = range(-1, 2)

    def __init__(
        self,
        searcher1: CombinatorialSpecificationSearcher,
        searcher2: CombinatorialSpecificationSearcher,
        atom_equals: Callable[[CombinatorialClass, CombinatorialClass], bool],
    ):
        self.pi1 = ParallelInfo(searcher1)
        self.pi2 = ParallelInfo(searcher2)
        self._ancestors: Set[Tuple[int, int]] = set()
        self.atom_equals = atom_equals

    def find(
        self,
    ) -> Optional[Tuple[CombinatorialSpecification, CombinatorialSpecification]]:
        """Find bijections between the two universes."""
        matching_info: MATCHING_INFO = {}
        visited: Set[Tuple[int, int]] = set()
        found = self._find(
            self.pi1.root_eq_label, self.pi2.root_eq_label, matching_info, visited
        )
        return self._matching_info_to_specs(found, matching_info)

    def _find(
        self,
        id1: int,
        id2: int,
        matching_info: MATCHING_INFO,
        visited: Set[Tuple[int, int]],
    ) -> bool:
        # pylint: disable=too-many-nested-blocks
        known = self._base_case(id1, id2, matching_info, visited)
        if known:
            return bool(known + 1)

        self._ancestors.add((id1, id2))

        found = False
        for rule_type, child_cnt_map in self.pi1.eq_label_rules[id1].items():
            # If attempted match has no rule of this type they won't match
            if rule_type not in self.pi2.eq_label_rules[id2]:
                continue

            # Try matching of all children with the children in the other spec.
            # This is done with a non-recursive backtracking.
            for n, child_set in child_cnt_map.items():
                for children2 in self.pi2.eq_label_rules[id2][rule_type][n]:
                    for children1 in child_set:
                        stack = [(0, i, {i}) for i in range(n - 1, -1, -1)]
                        while stack:
                            i1, i2, in_use = stack.pop()
                            if not self._find(
                                children1[i1], children2[i2], matching_info, visited
                            ):
                                continue
                            if i1 == n - 1:
                                if (id1, id2) not in matching_info:
                                    matching_info[(id1, id2)] = set()
                                matching_info[(id1, id2)].add((children1, children2))
                                found = True
                                break
                            for i in range(n - 1, -1, -1):
                                if i in in_use:
                                    continue
                                stack.append((i1 + 1, i, in_use.union({i})))
        self._ancestors.remove((id1, id2))
        visited.add((id1, id2))
        return found

    def _base_case(
        self,
        id1: int,
        id2: int,
        matching_info: MATCHING_INFO,
        visited: Set[Tuple[int, int]],
    ) -> int:
        # If rule type has no constructor we compare atoms
        if NO_CONSTRUCTOR in self.pi1.eq_label_rules[id1]:
            if NO_CONSTRUCTOR in self.pi2.eq_label_rules[id2]:
                if self.atom_equals(self.pi1.atom_map[id1], self.pi2.atom_map[id2]):
                    matching_info[(id1, id2)] = {((), ())}
                    return ParallelSpecFinder._VALID
                if len(self.pi2.eq_label_rules[id2]) == 1:
                    return ParallelSpecFinder._INVALID
            if len(self.pi1.eq_label_rules[id1]) == 1:
                return ParallelSpecFinder._INVALID

        if (id1, id2) in matching_info:
            return ParallelSpecFinder._VALID
        if (id1, id2) in visited:
            return ParallelSpecFinder._INVALID
        if (id1, id2) in self._ancestors:
            return ParallelSpecFinder._VALID
        return ParallelSpecFinder._UNKNOWN

    def _matching_info_to_specs(
        self,
        found: bool,
        matching_info: MATCHING_INFO,
    ) -> Optional[Tuple[CombinatorialSpecification, CombinatorialSpecification]]:
        if not found:
            return None
        spec_rules = self._search_matching_info(matching_info)
        if spec_rules is None:
            return None

        """sp1: Dict[int, Tuple[int, ...]] = {}
        sp2: Dict[int, Tuple[int, ...]] = {}
        for k, v in matching_info.items():
            (a, b), (c, d) = k, v
            sp1[a], sp2[b] = c, d"""
        return (
            ParallelSpecFinder._create_spec(spec_rules[0], self.pi1),
            ParallelSpecFinder._create_spec(spec_rules[1], self.pi2),
        )

    def _search_matching_info(
        self, matching_info: MATCHING_INFO
    ) -> Optional[Tuple[Dict[int, Tuple[int, ...]], Dict[int, Tuple[int, ...]]]]:
        matching_info_1 = {}
        matching_info_2 = {}
        for (p1, p2), children in matching_info.items():
            if p1 not in matching_info_1:
                matching_info_1[p1] = {}
            if p2 not in matching_info_2:
                matching_info_2[p2] = {}
            matching_info_1[p1][p2] = set()
            matching_info_2[p2][p1] = set()
            for ch1, ch2 in children:
                matching_info_1[p1][p2].add(ch1)
                matching_info_2[p2][p1].add(ch2)

        sp1: Dict[int, Tuple[int, ...]] = {}
        sp2: Dict[int, Tuple[int, ...]] = {}

        # visisted: Set[Tuple[int, int, Tuple[int, ...], Tuple[int, ...]]] = set()

        def _rec(id1: int, id2: int, ids_set1: Set[int], ids_set2: Set[int]) -> bool:
            if (id1, id2) not in matching_info:
                return False
            if matching_info[(id1, id2)] == {((), ())}:
                sp1[id1] = ()  # TODO: Not needed as we default to () from this dict
                sp2[id2] = ()
                return True
            if id1 in sp1 and id2 in sp2:
                return True
            if id1 in sp1 and sp1[id1] not in matching_info_1[id1][id2]:
                return False
            if id2 in sp2 and sp2[id2] not in matching_info_2[id2][id1]:
                return False
            # if one id is in sp, we only want the matching children
            # TODO: do that more efficiently
            for children1, children2 in matching_info[(id1, id2)]:
                if id1 in sp1 and children1 != sp1[id1]:
                    continue
                if id2 in sp2 and children2 != sp2[id2]:
                    continue
                sp1[id1] = children1
                sp2[id2] = children2
                to_clean_1, to_clean_2 = set(), set()
                if all(
                    _rec(child1, child2, to_clean_1, to_clean_2)
                    for child1, child2 in filter(
                        lambda m: m in matching_info, product(children1, children2)
                    )
                ):
                    ids_set1.add(id1)
                    ids_set2.add(id2)
                    return True
                for i in to_clean_1:
                    if i in sp1:
                        del sp1[i]
                for i in to_clean_2:
                    if i in sp2:
                        del sp2[i]
                if id1 in sp1:
                    del sp1[id1]
                if id2 in sp2:
                    del sp2[id2]

            return False

        if _rec(self.pi1.root_eq_label, self.pi1.root_eq_label, set(), set()):
            return sp1, sp2

        return None

    @staticmethod
    def _create_spec(
        d: Dict[int, Tuple[int, ...]], pi: ParallelInfo
    ) -> CombinatorialSpecification:
        visited: Set[int] = set()
        root_node = Node(pi.root_eq_label)
        queue = deque([root_node])
        while queue:
            v = queue.popleft()
            rule = d.get(v.label, ())
            if not (v.label in visited or rule == ()):
                children = [Node(i) for i in rule]
                queue.extend(children)
                v.children = children
            visited.add(v.label)
        rules = SpecificationRuleExtractor(
            pi.root_eq_label, root_node, pi.r_db, pi.searcher.classdb
        ).rules()
        return CombinatorialSpecification(pi.root_class, rules)


def _default_equals(c1: CombinatorialClass, c2: CombinatorialClass) -> bool:
    return c1 == c2


def find_bijection_between(
    searcher1: CombinatorialSpecificationSearcher,
    searcher2: CombinatorialSpecificationSearcher,
    atom_equals: Callable[
        [CombinatorialClass, CombinatorialClass], bool
    ] = _default_equals,
) -> Optional[Tuple[CombinatorialSpecification, CombinatorialSpecification]]:
    """Find bijections between two universes. If they are not of the same type, a
    custom atom comparator is needed."""
    return ParallelSpecFinder(searcher1, searcher2, atom_equals).find()
