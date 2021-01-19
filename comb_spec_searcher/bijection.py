from collections import defaultdict, deque
from typing import DefaultDict, Dict, List, Optional, Set, Tuple

from comb_spec_searcher.comb_spec_searcher import CombinatorialSpecificationSearcher
from comb_spec_searcher.combinatorial_class import CombinatorialClass
from comb_spec_searcher.rule_db.base import RuleDBBase
from comb_spec_searcher.specification import CombinatorialSpecification
from comb_spec_searcher.specification_extrator import SpecificationRuleExtractor
from comb_spec_searcher.strategies.rule import Rule
from comb_spec_searcher.tree_searcher import Node, prune
from comb_spec_searcher.typing import RuleKey

NO_CONSTRUCTOR = None.__class__


class ParallelInfo:
    def __init__(self, searcher: CombinatorialSpecificationSearcher):
        self.searcher: CombinatorialSpecificationSearcher = searcher
        while searcher.get_specification(minimization_time_limit=0) is None:
            searcher.do_level()
        self.r_db: RuleDBBase = self.searcher.ruledb
        self.rule_dict: Dict[
            int, Set[Tuple[int, ...]]
        ] = self.r_db.rules_up_to_equivalence()
        prune(self.rule_dict)
        self.root_label: int = self.searcher.start_label
        self.root_eq_label: int = self.r_db.equivdb[self.root_label]
        self.atom_map: Dict[int, CombinatorialClass] = {}
        self.root_class: Optional[CombinatorialClass] = None
        self.eq_label_rules: DefaultDict[
            int, DefaultDict[type, DefaultDict[int, Set[Tuple[int, ...]]]]
        ] = self._construct_eq_label_rules()

    def _construct_eq_label_rules(
        self,
    ) -> DefaultDict[int, DefaultDict[type, DefaultDict[int, Set[Tuple[int, ...]]]]]:
        # TODO: From how this is used in css, this should rly be a set
        # but currently a list is expected.
        lis: List[Tuple[int, Tuple[int, ...]]] = [
            (k, c) for k, v in self.rule_dict.items() for c in v
        ]
        rule_dict: Dict[RuleKey, RuleKey] = self.r_db.rule_from_equivalence_rule_dict(
            lis
        )
        eq_label_rules: DefaultDict[
            int, DefaultDict[type, DefaultDict[int, Set[Tuple[int, ...]]]]
        ] = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))

        for eq_par, eq_chi in lis:
            actual_par, actual_children = rule_dict[(eq_par, eq_chi)]
            strategy = self.r_db.rule_to_strategy[(actual_par, actual_children)]
            parent = self.searcher.classdb.get_class(actual_par)
            children = tuple(map(self.searcher.classdb.get_class, actual_children))
            rule = strategy(parent, children)
            if eq_par == self.root_eq_label and self.root_class is None:
                self.root_class = parent
            if parent.is_atom():
                eq_label_rules[eq_par][NO_CONSTRUCTOR][len(children)].add(eq_chi)
                self.atom_map[eq_par] = parent
            else:
                assert isinstance(rule, Rule)
                eq_label_rules[eq_par][rule.constructor.__class__][len(children)].add(
                    eq_chi
                )
        return eq_label_rules


class ParallelSpecFinder:

    _INVALID, _UNKNOWN, _VALID = range(-1, 2)

    def __init__(
        self,
        searcher1: CombinatorialSpecificationSearcher,
        searcher2: CombinatorialSpecificationSearcher,
    ):
        self.pi1 = ParallelInfo(searcher1)
        self.pi2 = ParallelInfo(searcher2)
        self.a_label: int = 0
        self.a1: Dict[int, int] = {}
        self.a2: Dict[int, int] = {}

    def find(
        self,
    ) -> Optional[Tuple[CombinatorialSpecification, CombinatorialSpecification]]:
        matching_info: Dict[
            Tuple[int, int], Tuple[Tuple[int, ...], Tuple[int, ...]]
        ] = {}
        visited: Set[Tuple[int, int]] = set()
        print("Starting search", flush=True)
        found = self._find(
            self.pi1.root_eq_label, self.pi2.root_eq_label, matching_info, visited
        )
        return self._matching_info_to_specs(found, matching_info)

    def _find(
        self,
        id1: int,
        id2: int,
        matching_info: Dict[Tuple[int, int], Tuple[Tuple[int, ...], Tuple[int, ...]]],
        visited: Set[Tuple[int, int]],
    ) -> bool:
        # pylint: disable=too-many-nested-blocks

        known = self._base_case(id1, id2, matching_info, visited)
        if known:
            return bool(known + 1)

        self._set_labels(id1, id2)

        for rule_type, child_cnt_map in self.pi1.eq_label_rules[id1].items():
            # If attempted match has no rule of this type they won't match
            if rule_type not in self.pi2.eq_label_rules[id2]:
                continue
            # If rule type has no constructor we compare atoms
            if rule_type == NO_CONSTRUCTOR:
                # TODO: add optional custom atom comparison
                if self.pi1.atom_map[id1] == self.pi2.atom_map[id2]:
                    matching_info[(id1, id2)] = ((), ())
                    return True
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
                                matching_info[(id1, id2)] = (children1, children2)
                                return True
                            for i in range(n - 1, -1, -1):
                                if i in in_use:
                                    continue
                                stack.append((i1 + 1, i, in_use.union({i})))
        self._clean_labels(id1, id2)
        visited.add((id1, id2))
        return False

    def _base_case(
        self,
        id1: int,
        id2: int,
        matching_info: Dict[Tuple[int, int], Tuple[Tuple[int, ...], Tuple[int, ...]]],
        visited: Set[Tuple[int, int]],
    ) -> int:
        if (id1, id2) in matching_info:
            return ParallelSpecFinder._VALID
        if (id1, id2) in visited:
            return ParallelSpecFinder._INVALID
        a1, a2 = self.a1.get(id1, -1), self.a2.get(id2, -1)
        if a1 == a2 == -1:
            return ParallelSpecFinder._UNKNOWN
        if a1 == a2:
            return ParallelSpecFinder._VALID
        return ParallelSpecFinder._INVALID

    def _set_labels(self, id1: int, id2: int):
        self.a_label += 1
        self.a1[id1], self.a2[id2] = (self.a_label, self.a_label)

    def _clean_labels(self, id1: int, id2: int):
        del self.a1[id1]
        del self.a2[id2]
        self.a_label -= 1

    def _matching_info_to_specs(
        self,
        found: bool,
        matching_info: Dict[Tuple[int, int], Tuple[Tuple[int, ...], Tuple[int, ...]]],
    ) -> Optional[Tuple[CombinatorialSpecification, CombinatorialSpecification]]:
        if not found:
            return None
        sp1, sp2 = {}, {}
        for k, v in matching_info.items():
            a, b = k
            c, d = v
            sp1[a] = c
            sp2[b] = d
        return (
            ParallelSpecFinder._create_spec(sp1, self.pi1),
            ParallelSpecFinder._create_spec(sp2, self.pi2),
        )

    @staticmethod
    def _create_spec(
        d: Dict[int, Tuple[int, ...]], pi: ParallelInfo
    ) -> CombinatorialSpecification:
        visited: Set[int] = set()
        root_node = Node(pi.root_eq_label)
        queue = deque([root_node])
        while queue:
            v = queue.popleft()
            rule = d[v.label]
            if not (v.label in visited or rule == ()):
                children = [Node(i) for i in rule]
                queue.extend(children)
                v.children = children
            visited.add(v.label)
        rules = SpecificationRuleExtractor(
            pi.root_eq_label, root_node, pi.r_db, pi.searcher.classdb
        ).rules()
        return CombinatorialSpecification(pi.root_class, rules)