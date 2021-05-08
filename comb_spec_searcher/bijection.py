from collections import defaultdict, deque
from typing import (
    TYPE_CHECKING,
    DefaultDict,
    Dict,
    Generic,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
)

from comb_spec_searcher.comb_spec_searcher import CombinatorialSpecificationSearcher
from comb_spec_searcher.exception import NoMoreClassesToExpandError
from comb_spec_searcher.specification import CombinatorialSpecification
from comb_spec_searcher.specification_extrator import (
    EquivalenceRuleExtractor,
    SpecificationRuleExtractor,
)
from comb_spec_searcher.strategies.constructor.base import Constructor
from comb_spec_searcher.strategies.rule import AbstractRule, Rule
from comb_spec_searcher.tree_searcher import Node, prune
from comb_spec_searcher.typing import (
    CombinatorialClassType,
    CombinatorialObjectType,
    RuleKey,
    Terms,
)

if TYPE_CHECKING:
    from comb_spec_searcher.combinatorial_class import (
        CombinatorialClass,
        CombinatorialObject,
    )


ClassType1 = TypeVar("ClassType1", bound="CombinatorialClass")
ObjType1 = TypeVar("ObjType1", bound="CombinatorialObject")
ClassType2 = TypeVar("ClassType2", bound="CombinatorialClass")
ObjType2 = TypeVar("ObjType2", bound="CombinatorialObject")
NO_CONSTRUCTOR = None.__class__
MatchingInfo = DefaultDict[
    Tuple[int, int], Dict[Tuple[Tuple[int, ...], Tuple[int, ...]], List[int]]
]
MatchingInfoSingle = DefaultDict[int, DefaultDict[int, Set[Tuple[int, ...]]]]
SpecMap = Dict[int, Tuple[int, ...]]
RuleClassification = DefaultDict[
    int,
    DefaultDict[
        int,
        List[
            Tuple[
                Tuple[int, ...],
                Union[
                    Constructor[CombinatorialClassType, CombinatorialObjectType],
                    None,
                ],
            ]
        ],
    ],
]
EqPathTracker = DefaultDict[
    Tuple[int, int],
    DefaultDict[
        Tuple[int, int],
        Dict[Tuple[Tuple[int, ...], Tuple[int, ...]], bool],
    ],
]


class ParallelInfo(Generic[CombinatorialClassType, CombinatorialObjectType]):
    """Information from searcher essential to finding bijection with another and then
    to create specifications.
    """

    def __init__(
        self,
        searcher: CombinatorialSpecificationSearcher[CombinatorialClassType],
        additional_levels: int = 0,
    ):
        self.searcher = searcher
        self._expand(additional_levels)

        # Root eq label and actual class
        self.root_eq_label: int = self.searcher.ruledb.equivdb[
            self.searcher.start_label
        ]
        self.root_class = self.searcher.classdb.get_class(self.searcher.start_label)

        # Atom information for comparing them
        self.atom_map: Dict[int, Tuple[int, Terms]] = {}

        # Used to filter out impossible matchings to avoid unnecessary expansions
        self.eq_label_rules = self._construct_eq_label_rules()

    def _expand(self, additional_levels: int) -> None:
        """Expand until at least one spec exists and after that some
        additional expansions can be done (optionally)."""
        self._expand_until_spec()
        self._additional_expands(additional_levels)

    def _expand_until_spec(self) -> None:
        try:
            while self.searcher.get_specification(minimization_time_limit=0) is None:
                self.searcher.do_level()
        except NoMoreClassesToExpandError as ex:
            if self.searcher.get_specification(minimization_time_limit=0) is None:
                raise ValueError("No specifications were found") from ex

    def _additional_expands(self, additional_levels: int) -> None:
        try:
            for _ in range(additional_levels):
                self.searcher.do_level()
        except NoMoreClassesToExpandError:
            pass

    def _construct_eq_label_rules(
        self,
    ) -> RuleClassification[CombinatorialClassType, CombinatorialObjectType]:
        """
        Creates a dictionary d such that
            d[eq_label][child_count]
        is a set of possible resulting children eq_labels and the corresponding
        constructor if any.
        """
        lis = self._pruned_rules_up_to_eq()
        rule_dict = self.searcher.ruledb.rule_from_equivalence_rule_dict(lis)
        eq_label_rules: RuleClassification[
            CombinatorialClassType, CombinatorialObjectType
        ] = defaultdict(lambda: defaultdict(list))

        for eq_par, eq_chi in lis:
            parent, rule = self._get_class_and_rule(eq_par, eq_chi, rule_dict)
            if parent.is_atom():
                eq_label_rules[eq_par][0].append((eq_chi, None))
                sz = next(
                    parent.objects_of_size(parent.minimum_size_of_object())
                ).size()
                self.atom_map[eq_par] = (sz, rule.get_terms(sz))
            else:
                if not isinstance(rule, Rule):
                    raise ValueError("Only atoms can be verified.")
                assert len(eq_chi) > 0
                eq_label_rules[eq_par][len(eq_chi)].append((eq_chi, rule.constructor))
        return eq_label_rules

    def _get_class_and_rule(
        self, eq_par: int, eq_chi: Tuple[int, ...], rule_dict: Dict[RuleKey, RuleKey]
    ) -> Tuple[
        CombinatorialClassType,
        AbstractRule[CombinatorialClassType, CombinatorialObjectType],
    ]:
        actual_par, actual_children = rule_dict[(eq_par, eq_chi)]
        strategy = self.searcher.ruledb.rule_to_strategy[(actual_par, actual_children)]
        parent = self.searcher.classdb.get_class(actual_par)
        rule: AbstractRule[CombinatorialClassType, CombinatorialObjectType] = strategy(
            parent
        )
        return parent, rule

    def _pruned_rules_up_to_eq(
        self,
    ) -> List[Tuple[int, Tuple[int, ...]]]:
        rules_up_to_eq = self.searcher.ruledb.rules_up_to_equivalence()
        prune(rules_up_to_eq)
        return [(k, c) for k, v in rules_up_to_eq.items() for c in v]


class ParallelSpecFinder(Generic[ClassType1, ObjType1, ClassType2, ObjType2]):
    """
    Finder for paralell specs. This version assumes that any classes that share
    equivalence labels are in fact equivalent.
    """

    _INVALID, _UNKNOWN, _VALID = range(-1, 2)

    def __init__(
        self,
        searcher1: CombinatorialSpecificationSearcher[ClassType1],
        searcher2: CombinatorialSpecificationSearcher[ClassType2],
    ):
        self._pre_expand(searcher1, searcher2)
        self._pi1 = ParallelInfo[ClassType1, ObjType1](searcher1)
        self._pi2 = ParallelInfo[ClassType2, ObjType2](searcher2)
        self._ancestors: Set[Tuple[int, int]] = set()

    def _pre_expand(
        self,
        searcher1: CombinatorialSpecificationSearcher[ClassType1],
        searcher2: CombinatorialSpecificationSearcher[ClassType2],
    ) -> None:
        """When overwritten, this method can be implemented and will be called
        prior to the searcher expanding the universe."""

    # First search

    def find(
        self,
    ) -> Optional[
        Tuple[
            CombinatorialSpecification[ClassType1, ObjType1],
            CombinatorialSpecification[ClassType2, ObjType2],
        ]
    ]:
        """Find bijections between the two universes."""
        # d[(p1,p2)][(c1,c2)] = permutation of children such that they match
        matching_info: MatchingInfo = defaultdict(dict)

        # Failed matches
        visited: Set[Tuple[int, int]] = set()

        # Find matching eq lables
        found = self._find(
            self._pi1.root_eq_label, self._pi2.root_eq_label, matching_info, visited
        )

        # Try to construct valid specs from said eq-label matchings
        return self._matching_info_to_specs(found, matching_info)

    def _find(
        self,
        id1: int,
        id2: int,
        matching_info: MatchingInfo,
        visited: Set[Tuple[int, int]],
    ) -> bool:
        """Recursion call to find matching for eq labels (id1,id2)."""

        # Check for base cases (invalid = -1, valid = 1)
        known = self._base_case(id1, id2, matching_info, visited)
        if known:
            return bool(known + 1)

        # Store pair as ancestors ids checked with further recursions
        self._ancestors.add((id1, id2))

        for children1, children2, n in self._potential_children(id1, id2):
            # The permutation of matched children indices
            child_order: List[int] = [-1] * n

            # Iterative stack with elements:
            # (index1, index2, indices of the second rule's children already matched)
            stack = [(0, i, {i}) for i in range(n - 1, -1, -1)]

            # To avoid repeated index pairs, since outside choices have no effect.
            blacklist: Set[Tuple[int, int]] = set()

            # Check all pairings of children. Any pairing hat exhaust all nonempty
            # children, such that all are valid will result in current nodes being
            # matched. This is done with backtracking.
            while stack:
                i1, i2, in_use = stack.pop()

                # Already failed
                if (i1, i2) in blacklist:
                    continue

                # Recursion. Blacklist children pair if we fail.
                if not self._find(children1[i1], children2[i2], matching_info, visited):
                    blacklist.add((i1, i2))
                    continue

                # Update permutation
                child_order[i2] = i1

                # If we reach the last index we have succeeded. Gather this matching and
                # keep trying other children as we want to collect all that are valid.
                if i1 == n - 1:
                    matching_info[(id1, id2)][(children1, children2)] = child_order
                    break

                # Extand stack if we are not done.
                ParallelSpecFinder._extend_stack(i1, n, in_use, stack)

        # Remove self as ancestors if we are done.
        self._ancestors.remove((id1, id2))

        # Store pair in memory of failures.
        visited.add((id1, id2))

        # Return true if any valid matching was found.
        return (id1, id2) in matching_info

    def _base_case(
        self,
        id1: int,
        id2: int,
        matching_info: MatchingInfo,
        visited: Set[Tuple[int, int]],
    ) -> int:
        # If no children we compare atoms
        if (
            id1 in self._pi1.atom_map
            and id2 in self._pi2.atom_map
            and self._atom_match(id1, id2)
        ):
            matching_info[(id1, id2)] = {((), ()): []}
            return ParallelSpecFinder._VALID

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

    def _atom_match(self, id1: int, id2: int) -> bool:
        """Returns true if atoms match."""
        sz1, terms1 = self._pi1.atom_map[id1]
        sz2, terms2 = self._pi2.atom_map[id2]
        return sz1 == sz2 and terms1 == terms2

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

    # Second search

    def _matching_info_to_specs(
        self,
        found: bool,
        matching_info: MatchingInfo,
    ) -> Optional[
        Tuple[
            CombinatorialSpecification[ClassType1, ObjType1],
            CombinatorialSpecification[ClassType2, ObjType2],
        ]
    ]:
        # If first search was unsuccessful
        if not found:
            return None
        # Attempt to construct specifications from matches
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
        # Matching info 1 and 2 are flatten dictionaries of matching_info
        # for the perspective of each spec. The maps sp1 and sp2 are the
        # gathered specifications (in terms of eq labels), initially empty.
        (
            matching_info1,
            matching_info2,
            sp1,
            sp2,
        ) = ParallelSpecFinder._search_matching_info_init(matching_info)

        # Recursive helper function that tries to populate the spec maps in a way
        # that no label appears on the LHS more than one time.
        def _rec(
            id1: int,
            id2: int,
            id_sets: Tuple[Set[int], Set[int]],
        ) -> bool:
            # Check base cases (invalid = -1, valid = 1)
            bc = ParallelSpecFinder._search_matching_info_recursion_base_cases(
                id1, id2, matching_info, matching_info1, matching_info2, sp1, sp2
            )
            if bc:
                return bool(bc + 1)

            # If ids have appeared before, we don't want to clean them when done
            rec1, rec2 = id1 in sp1, id2 in sp2

            # For all children that matches for given parent pair where they are either
            # not in spec maps or they are mapped to the children we are looking at.
            for children1, children2 in filter(
                lambda c: (id1 not in sp1 or c[0] == sp1[id1])
                and (id2 not in sp2 or c[1] == sp2[id2]),
                matching_info[(id1, id2)],
            ):
                # Add rule for spec to (id -> children) for both specs
                sp1[id1], sp2[id2] = children1, children2

                # Construct cleaning sets that are passed down the recursion
                to_clean: Tuple[Set[int], Set[int]] = (set(), set())

                # If all the children are valid, compared one at a time in the order
                # they were matched in the first search.
                if all(
                    _rec(child1, child2, to_clean)
                    for child1, child2 in zip(
                        (
                            children1[i]
                            for i in matching_info[(id1, id2)][(children1, children2)]
                        ),
                        children2,
                    )
                ):
                    # Update the cleaning set so any failing ancestor can remove.
                    id_sets[0].update(to_clean[0], () if rec1 else (id1,))
                    id_sets[1].update(to_clean[1], () if rec2 else (id2,))
                    return True
                # If failed, remove all descendants that populated the spec maps.
                ParallelSpecFinder._clean_descendants(
                    *to_clean, id1, id2, sp1, sp2, rec1, rec2
                )
            return False

        if _rec(
            self._pi1.root_eq_label,
            self._pi2.root_eq_label,
            (set(), set()),
        ):
            return sp1, sp2
        return None

    @staticmethod
    def _search_matching_info_init(
        matching_info: MatchingInfo,
    ) -> Tuple[MatchingInfoSingle, MatchingInfoSingle, SpecMap, SpecMap]:
        matching_info_1: MatchingInfoSingle = defaultdict(lambda: defaultdict(set))
        matching_info_2: MatchingInfoSingle = defaultdict(lambda: defaultdict(set))
        # convert (p1,p2) -> children to p1 -> p2 -> children and p2-> p1 -> children.
        for (p1, p2), children in matching_info.items():
            for ch1, ch2 in children:
                matching_info_1[p1][p2].add(ch1)
                matching_info_2[p2][p1].add(ch2)
        sp1: SpecMap = {}
        sp2: SpecMap = {}
        return matching_info_1, matching_info_2, sp1, sp2

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
        if ParallelSpecFinder._inconsistent_with_matching_info(
            id1, id2, matching_info, matching_info1, matching_info2, sp1, sp2
        ):
            return ParallelSpecFinder._INVALID
        # If atoms, there is only one possible outcome
        if ((), ()) in matching_info[(id1, id2)]:
            sp1[id1], sp2[id2] = (), ()
            return ParallelSpecFinder._VALID
        # If both are assigned, we are done
        if id1 in sp1 and id2 in sp2:
            return ParallelSpecFinder._VALID
        return ParallelSpecFinder._UNKNOWN

    @staticmethod
    def _inconsistent_with_matching_info(
        id1: int,
        id2: int,
        matching_info: MatchingInfo,
        matching_info1: MatchingInfoSingle,
        matching_info2: MatchingInfoSingle,
        sp1: SpecMap,
        sp2: SpecMap,
    ):
        """If ids are not in the matching order or if one is assigned but those
        children aren't compatible with the other.
        """
        return (
            (id1, id2) not in matching_info
            or (id1 in sp1 and sp1[id1] not in matching_info1[id1][id2])
            or (id2 in sp2 and sp2[id2] not in matching_info2[id2][id1])
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
        # Clean descendants
        for i in to_clean1:
            if i in sp1:
                del sp1[i]
        for i in to_clean2:
            if i in sp2:
                del sp2[i]
        # Clean self if no prior assignments
        if not rec1 and id1 in sp1:
            del sp1[id1]
        if not rec2 and id2 in sp2:
            del sp2[id2]

    # specification construction helpers

    @staticmethod
    def _create_spec(d: SpecMap, pi: ParallelInfo) -> CombinatorialSpecification:
        rules = SpecificationRuleExtractor(
            pi.root_eq_label,
            ParallelSpecFinder._create_tree(d, pi.root_eq_label),
            pi.searcher.ruledb,
            pi.searcher.classdb,
        ).rules()
        return CombinatorialSpecification(pi.root_class, rules)

    @staticmethod
    def _create_tree(d: SpecMap, root_eq_label: int) -> Node:
        visited: Set[int] = set()
        root_node = Node(root_eq_label)
        queue = deque([root_node])
        # BFS to consume spec map.
        while queue:
            v = queue.popleft()
            rule = d.get(v.label, ())
            if not (v.label in visited or rule == ()):
                children = [Node(i) for i in rule]
                queue.extend(children)
                v.children = children
            visited.add(v.label)
        return root_node


class EqPathParallelSpecFinder(
    ParallelSpecFinder[ClassType1, ObjType1, ClassType2, ObjType2]
):
    """
    A version of ParallelSpecFinder that supports nonequivalent
    classes sharing equivalence labels.
    """

    def __init__(
        self,
        searcher1: CombinatorialSpecificationSearcher[ClassType1],
        searcher2: CombinatorialSpecificationSearcher[ClassType2],
    ):
        super().__init__(searcher1, searcher2)

        # Tracks the path taken in the second search
        self._path: List[Tuple[int, int, int, int]] = [(-1, -1, -1, -1)]

    def _search_matching_info(
        self, matching_info: MatchingInfo
    ) -> Optional[Tuple[SpecMap, SpecMap]]:
        # This will differ (from super's) that equiv lables must
        # be validated given the path that has been taken.

        (
            matching_info1,
            matching_info2,
            sp1,
            sp2,
        ) = EqPathParallelSpecFinder._search_matching_info_init(matching_info)

        # For storing results of eq path checking.
        eq_path_tracker: EqPathTracker = defaultdict(lambda: defaultdict(dict))

        def _rec(
            id1: int,
            id2: int,
            id_sets: Tuple[Set[int], Set[int]],
        ) -> bool:
            bc = self._search_matching_info_recursion_base_cases_eq(
                id1,
                id2,
                matching_info,
                matching_info1,
                matching_info2,
                sp1,
                sp2,
                self._path[-1],
                eq_path_tracker,
            )
            if bc:
                return bool(bc + 1)
            rec1, rec2 = id1 in sp1, id2 in sp2
            for children1, children2 in filter(
                lambda c: (id1 not in sp1 or c[0] == sp1[id1])
                and (id2 not in sp2 or c[1] == sp2[id2]),
                matching_info[(id1, id2)],
            ):
                sp1[id1], sp2[id2] = children1, children2
                to_clean: Tuple[Set[int], Set[int]] = (set(), set())

                # Check if the path required for the eq labels actually matches
                if self._eq_path_matches(
                    id1, id2, *self._path[-1], sp1, sp2, eq_path_tracker
                ):
                    valid = True
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
                    ):
                        self._path.append((id1, id2, j1, j2))
                        if not _rec(child1, child2, to_clean):
                            valid = False
                            self._path.pop()
                            break
                        self._path.pop()
                    if valid:
                        id_sets[0].update(to_clean[0], () if rec1 else (id1,))
                        id_sets[1].update(to_clean[1], () if rec2 else (id2,))
                        return True
                EqPathParallelSpecFinder._clean_descendants(
                    *to_clean, id1, id2, sp1, sp2, rec1, rec2
                )
            return False

        if _rec(
            self._pi1.root_eq_label,
            self._pi2.root_eq_label,
            (set(), set()),
        ):
            return sp1, sp2
        return None

    def _search_matching_info_recursion_base_cases_eq(
        self,
        id1: int,
        id2: int,
        matching_info: MatchingInfo,
        matching_info1: MatchingInfoSingle,
        matching_info2: MatchingInfoSingle,
        sp1: SpecMap,
        sp2: SpecMap,
        relations: Tuple[int, int, int, int],
        eq_path_tracker: EqPathTracker,
    ) -> int:
        pid1, pid2, idx1, idx2 = relations
        if EqPathParallelSpecFinder._inconsistent_with_matching_info(
            id1, id2, matching_info, matching_info1, matching_info2, sp1, sp2
        ):
            return EqPathParallelSpecFinder._INVALID
        # These atoms will have matches in the first searcher but we do offer
        # additional checks which will, by default, always return true.
        if ((), ()) in matching_info[(id1, id2)]:
            if not self._atom_path_match(id1, id2):
                return EqPathParallelSpecFinder._INVALID
            sp1[id1], sp2[id2] = (), ()
            return EqPathParallelSpecFinder._VALID
        # If both ids are set we still need to check if they are valid in terms
        # of eq paths since we may have arrived from different parents.
        if id1 in sp1 and id2 in sp2:
            if self._eq_path_matches(
                id1, id2, pid1, pid2, idx1, idx2, sp1, sp2, eq_path_tracker
            ):
                return EqPathParallelSpecFinder._VALID
            return EqPathParallelSpecFinder._INVALID
        return EqPathParallelSpecFinder._UNKNOWN

    def _atom_path_match(self, id1: int, id2: int) -> bool:
        """This can be overwritten if the path can affect the validity of the pair."""
        # pylint: disable=no-self-use
        return True

    def _eq_path_matches(
        self,
        id1,
        id2,
        pid1,
        pid2,
        idx1: int,
        idx2: int,
        sp1: SpecMap,
        sp2: SpecMap,
        cache: EqPathTracker,
    ) -> bool:
        """
        Given (grandparent, parent, children) eq labels in both specs, this will check
        if the actual rules required (disregarding actual equivalence rules) to traverse
        this path match.
        """
        children = (sp1[id1], sp2[id2])
        children_cache = cache[(id1, id2)][(pid1, pid2)]
        if children not in children_cache:
            path1 = EquivalenceRuleExtractor(
                self._pi1.root_eq_label,
                self._pi1.searcher.start_label,
                EqPathParallelSpecFinder._create_tree(sp1, self._pi1.root_eq_label),
                self._pi1.searcher.ruledb,
                self._pi1.searcher.classdb,
                id1,
                pid1,
                idx1,
            ).nonequivalent_rules_in_equiv_path()
            path2 = EquivalenceRuleExtractor(
                self._pi2.root_eq_label,
                self._pi2.searcher.start_label,
                EqPathParallelSpecFinder._create_tree(sp2, self._pi2.root_eq_label),
                self._pi2.searcher.ruledb,
                self._pi2.searcher.classdb,
                id2,
                pid2,
                idx2,
            ).nonequivalent_rules_in_equiv_path()
            children_cache[children] = len(path1) == len(path2) and all(
                r1.constructor.equiv(r2.constructor)[0] for r1, r2 in zip(path1, path2)
            )
        return children_cache[children]
