from collections import defaultdict, deque
from typing import DefaultDict, Dict, List, Optional, Set, Tuple, Union

from comb_spec_searcher.comb_spec_searcher import CombinatorialSpecificationSearcher
from comb_spec_searcher.combinatorial_class import CombinatorialClass
from comb_spec_searcher.exception import NoMoreClassesToExpandError
from comb_spec_searcher.rule_db.base import RuleDBBase
from comb_spec_searcher.specification import CombinatorialSpecification
from comb_spec_searcher.specification_extrator import (
    EquivalenceRuleExtractor,
    SpecificationRuleExtractor,
)
from comb_spec_searcher.strategies.constructor.base import Constructor
from comb_spec_searcher.strategies.rule import Rule
from comb_spec_searcher.tree_searcher import Node, prune
from comb_spec_searcher.typing import RuleKey, Terms

NO_CONSTRUCTOR = None.__class__
MatchingInfo = DefaultDict[
    Tuple[int, int], Dict[Tuple[Tuple[int, ...], Tuple[int, ...]], List[int]]
]
MatchingInfoSingle = DefaultDict[int, DefaultDict[int, Set[Tuple[int, ...]]]]
SpecMap = Dict[int, Tuple[int, ...]]
RuleClassification = DefaultDict[
    int, DefaultDict[int, List[Tuple[Tuple[int, ...], Union[Constructor, None]]]]
]


class ParallelInfo:
    """Information from searcher essential to finding bijection with another and then
    to create specifications.
    """

    def __init__(self, searcher: CombinatorialSpecificationSearcher):
        self.searcher: CombinatorialSpecificationSearcher = searcher
        self._expand()
        self.r_db: RuleDBBase = self.searcher.ruledb
        self.root_eq_label: int = self.r_db.equivdb[self.searcher.start_label]
        self.atom_map: Dict[int, Tuple[int, Terms]] = {}
        self.root_class: CombinatorialClass = self.searcher.classdb.get_class(
            self.searcher.start_label
        )
        self.eq_label_rules: RuleClassification = self._construct_eq_label_rules()

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
    ) -> RuleClassification:
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
            rule = strategy(parent)
            if parent.is_atom():
                eq_label_rules[eq_par][0].append((eq_chi, None))
                sz = next(
                    parent.objects_of_size(parent.minimum_size_of_object())
                ).size()
                self.atom_map[eq_par] = (sz, rule.get_terms(sz))
            else:
                assert isinstance(rule, Rule)
                eq_label_rules[eq_par][len(eq_chi)].append((eq_chi, rule.constructor))
        return eq_label_rules

    def _construct_eq_labels_init(
        self,
    ) -> Tuple[
        List[Tuple[int, Tuple[int, ...]]],
        Dict[RuleKey, RuleKey],
        RuleClassification,
    ]:
        rules_up_to_eq = self.r_db.rules_up_to_equivalence()
        prune(rules_up_to_eq)
        lis = [(k, c) for k, v in rules_up_to_eq.items() for c in v]
        rule_dict = self.r_db.rule_from_equivalence_rule_dict(lis)
        eq_label_rules: RuleClassification = defaultdict(lambda: defaultdict(list))
        return lis, rule_dict, eq_label_rules


class ParallelSpecFinder:
    """Finder for paralell specs."""

    _INVALID, _UNKNOWN, _VALID = range(-1, 2)

    def __init__(
        self,
        searcher1: CombinatorialSpecificationSearcher,
        searcher2: CombinatorialSpecificationSearcher,
    ):
        self._pi1 = ParallelInfo(searcher1)
        self._pi2 = ParallelInfo(searcher2)
        self._ancestors: Set[Tuple[int, int]] = set()

    def find(
        self,
    ) -> Optional[Tuple[CombinatorialSpecification, CombinatorialSpecification]]:
        """Find bijections between the two universes."""
        matching_info: MatchingInfo = defaultdict(dict)
        visited: Set[Tuple[int, int]] = set()
        found = self._find(
            self._pi1.root_eq_label, self._pi2.root_eq_label, matching_info, visited
        )
        return self._matching_info_to_specs(found, matching_info)

    def _find(
        self,
        id1: int,
        id2: int,
        matching_info: MatchingInfo,
        visited: Set[Tuple[int, int]],
    ) -> bool:
        known = self._base_case(id1, id2, matching_info, visited)
        if known:
            return bool(known + 1)
        self._ancestors.add((id1, id2))
        found = False
        for children1, children2, n in self._potential_children(id1, id2):
            child_order: List[int] = [-1] * n
            stack = [(0, i, {i}) for i in range(n - 1, -1, -1)]
            blacklist: Set[Tuple[int, int]] = set()
            while stack:
                i1, i2, in_use = stack.pop()
                if (i1, i2) in blacklist:
                    continue
                if not self._find(children1[i1], children2[i2], matching_info, visited):
                    blacklist.add((i1, i2))
                    continue
                child_order[i2] = i1
                if i1 == n - 1:
                    matching_info[(id1, id2)][(children1, children2)] = child_order
                    found = True
                    break
                ParallelSpecFinder._extend_stack(i1, n, in_use, stack)
        self._ancestors.remove((id1, id2))
        visited.add((id1, id2))
        return found

    def _base_case(
        self,
        id1: int,
        id2: int,
        matching_info: MatchingInfo,
        visited: Set[Tuple[int, int]],
    ) -> int:
        # If rule type has no constructor we compare atoms
        if 0 in self._pi1.eq_label_rules[id1]:
            if 0 in self._pi2.eq_label_rules[id2]:
                sz1, terms1 = self._pi1.atom_map[id1]
                sz2, terms2 = self._pi2.atom_map[id2]
                if sz1 == sz2 and terms1 == terms2:
                    matching_info[(id1, id2)] = {((), ()): []}
                    return ParallelSpecFinder._VALID
                if len(self._pi2.eq_label_rules[id2]) == 1:
                    return ParallelSpecFinder._INVALID
            if len(self._pi1.eq_label_rules[id1]) == 1:
                return ParallelSpecFinder._INVALID
        # Already matched
        if (id1, id2) in matching_info:
            return ParallelSpecFinder._VALID
        # Already failed to match
        if (id1, id2) in visited:
            return ParallelSpecFinder._INVALID
        # Recursive match
        if (id1, id2) in self._ancestors:
            return ParallelSpecFinder._VALID
        return ParallelSpecFinder._UNKNOWN

    def _potential_children(
        self, id1: int, id2: int
    ) -> List[Tuple[Tuple[int, ...], Tuple[int, ...], int]]:
        """Children are potential children if all of the following holds they have the
        same number of non-empty children and the constructor's GF matches.
        """
        return [
            (c1, c2, n)
            for n, child_rule_pairs in self._pi1.eq_label_rules[id1].items()
            for c1, r1 in child_rule_pairs
            for c2, r2 in self._pi2.eq_label_rules[id2][n]
            if (r1 is None and r2 is None)
            or (r1 is not None and r2 is not None and r1.equiv(r2)[0])
        ]

    @staticmethod
    def _extend_stack(
        i1: int, n: int, in_use: Set[int], stack: List[Tuple[int, int, Set[int]]]
    ) -> None:
        for i in range(n - 1, -1, -1):
            if i in in_use:
                continue
            stack.append((i1 + 1, i, in_use.union({i})))

    def _matching_info_to_specs(
        self,
        found: bool,
        matching_info: MatchingInfo,
    ) -> Optional[Tuple[CombinatorialSpecification, CombinatorialSpecification]]:
        if not found:
            return None
        spec_rules = self._search_matching_info(matching_info)
        if spec_rules is None:
            return None
        return (
            ParallelSpecFinder._create_spec(spec_rules[0], self._pi1),
            ParallelSpecFinder._create_spec(spec_rules[1], self._pi2),
        )

    def _search_matching_info(
        self, matching_info: MatchingInfo
    ) -> Optional[Tuple[SpecMap, SpecMap]]:
        (
            matching_info1,
            matching_info2,
            sp1,
            sp2,
            eq_path_tracker,
        ) = ParallelSpecFinder._search_matching_info_init(matching_info)

        def _rec(
            id1: int,
            id2: int,
            pid1: int,
            pid2: int,
            idx1: int,
            idx2: int,
            id_sets: Tuple[Set[int], Set[int]],
        ) -> bool:
            bc = ParallelSpecFinder._search_matching_info_recursion_base_cases(
                id1, id2, matching_info, matching_info1, matching_info2, sp1, sp2
            )
            if bc:
                return bool(bc + 1)
            # TODO: move into base case
            if id1 in sp1 and id2 in sp2:
                if (pid1, pid2) in eq_path_tracker[(id1, id2)]:
                    return True
                if self._eq_path_matches(id1, id2, pid1, pid2, idx1, idx2, sp1, sp2)[0]:
                    return True
                return False
            rec1, rec2 = id1 in sp1, id2 in sp2
            for children1, children2 in filter(
                lambda c: (id1 not in sp1 or c[0] == sp1[id1])
                and (id2 not in sp2 or c[1] == sp2[id2]),
                matching_info[(id1, id2)],
            ):
                sp1[id1], sp2[id2] = children1, children2
                to_clean: Tuple[Set[int], Set[int]] = (set(), set())

                valid_eq, store = self._eq_path_matches(
                    id1, id2, pid1, pid2, idx1, idx2, sp1, sp2
                )
                if valid_eq:
                    if store:
                        eq_path_tracker[(id1, id2)].add((pid1, pid2))
                    if all(
                        _rec(child1, child2, id1, id2, j1, j2, to_clean)
                        for j2, ((j1, child1), child2) in enumerate(
                            zip(
                                (
                                    (i, children1[i])
                                    for i in matching_info[(id1, id2)][
                                        (children1, children2)
                                    ]
                                ),
                                children2,
                            )
                        )
                    ):
                        id_sets[0].update(to_clean[0], () if rec1 else (id1,))
                        id_sets[1].update(to_clean[1], () if rec2 else (id2,))
                        return True
                ParallelSpecFinder._clean_descendants(
                    *to_clean, id1, id2, sp1, sp2, rec1, rec2
                )
            return False

        if _rec(
            self._pi1.root_eq_label,
            self._pi2.root_eq_label,
            -1,
            -1,
            -1,
            -1,
            (set(), set()),
        ):
            return sp1, sp2
        return None

    @staticmethod
    def _search_matching_info_init(
        matching_info: MatchingInfo,
    ) -> Tuple[
        MatchingInfoSingle,
        MatchingInfoSingle,
        SpecMap,
        SpecMap,
        DefaultDict[Tuple[int, int], Set[Tuple[int, int]]],
    ]:
        matching_info_1: MatchingInfoSingle = defaultdict(lambda: defaultdict(set))
        matching_info_2: MatchingInfoSingle = defaultdict(lambda: defaultdict(set))
        for (p1, p2), children in matching_info.items():
            for ch1, ch2 in children:
                matching_info_1[p1][p2].add(ch1)
                matching_info_2[p2][p1].add(ch2)
        sp1: SpecMap = {}
        sp2: SpecMap = {}
        eq_path_tracker: DefaultDict[
            Tuple[int, int], Set[Tuple[int, int]]
        ] = defaultdict(set)
        return matching_info_1, matching_info_2, sp1, sp2, eq_path_tracker

    @staticmethod
    def _search_matching_info_recursion_base_cases(
        id1: int,
        id2: int,
        matching_info: MatchingInfo,
        matching_info1: MatchingInfoSingle,
        matching_info2: MatchingInfoSingle,
        sp1: SpecMap,
        sp2: SpecMap,
    ) -> int:
        if (id1, id2) not in matching_info:
            return ParallelSpecFinder._INVALID
        if ((), ()) in matching_info[(id1, id2)]:
            sp1[id1], sp2[id2] = (), ()
            return ParallelSpecFinder._VALID
        # if id1 in sp1 and id2 in sp2:
        #    return ParallelSpecFinder._VALID
        if id1 in sp1 and sp1[id1] not in matching_info1[id1][id2]:
            return ParallelSpecFinder._INVALID
        if id2 in sp2 and sp2[id2] not in matching_info2[id2][id1]:
            return ParallelSpecFinder._INVALID
        return ParallelSpecFinder._UNKNOWN

    def _eq_path_matches(
        self, id1, id2, pid1, pid2, idx1: int, idx2: int, sp1: SpecMap, sp2: SpecMap
    ) -> Tuple[bool, bool]:
        path1 = EquivalenceRuleExtractor(
            self._pi1.root_eq_label,
            self._pi1.searcher.start_label,
            ParallelSpecFinder._create_tree(sp1, self._pi1.root_eq_label),
            self._pi1.r_db,
            self._pi1.searcher.classdb,
            id1,
            pid1,
            idx1,
        ).nonequivalent_rules_in_equiv_path()
        path2 = EquivalenceRuleExtractor(
            self._pi2.root_eq_label,
            self._pi2.searcher.start_label,
            ParallelSpecFinder._create_tree(sp2, self._pi2.root_eq_label),
            self._pi2.r_db,
            self._pi2.searcher.classdb,
            id2,
            pid2,
            idx2,
        ).nonequivalent_rules_in_equiv_path()
        return (
            len(path1) == len(path2)
            and all(
                r1.constructor.equiv(r2.constructor)[0] for r1, r2 in zip(path1, path2)
            ),
            len(path1) > 0 and len(path2) > 0,
        )

    @staticmethod
    def _clean_descendants(
        to_clean1: Set[int],
        to_clean2: Set[int],
        id1: int,
        id2: int,
        sp1: SpecMap,
        sp2: SpecMap,
        rec1: bool,
        rec2: bool,
    ):
        for i in to_clean1:
            if i in sp1:
                del sp1[i]
        for i in to_clean2:
            if i in sp2:
                del sp2[i]
        if not rec1 and id1 in sp1:
            del sp1[id1]
        if not rec2 and id2 in sp2:
            del sp2[id2]

    @staticmethod
    def _create_spec(d: SpecMap, pi: ParallelInfo) -> CombinatorialSpecification:
        rules = SpecificationRuleExtractor(
            pi.root_eq_label,
            ParallelSpecFinder._create_tree(d, pi.root_eq_label),
            pi.r_db,
            pi.searcher.classdb,
        ).rules()
        return CombinatorialSpecification(pi.root_class, rules)

    @staticmethod
    def _create_tree(d: SpecMap, root_eq_label: int) -> Node:
        visited: Set[int] = set()
        root_node = Node(root_eq_label)
        queue = deque([root_node])
        while queue:
            v = queue.popleft()
            rule = d.get(v.label, ())
            if not (v.label in visited or rule == ()):
                children = [Node(i) for i in rule]
                queue.extend(children)
                v.children = children
            visited.add(v.label)
        return root_node
