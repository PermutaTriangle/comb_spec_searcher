"""
Finds and returns a combinatorial specification, that we call a proof tree.
"""
import time
from collections import defaultdict, deque
from copy import deepcopy
from itertools import chain, product
from random import choice, shuffle
from typing import Dict, FrozenSet, Iterator, List, Optional, Sequence, Set, Tuple

from comb_spec_searcher.typing import RulesDict

__all__ = ("prune", "proof_tree_generator_dfs", "proof_tree_generator_bfs")


class Node:
    """A node for a proof tree."""

    def __init__(self, n: int, children: Optional[List["Node"]] = None):
        if children is None:
            children = []
        self.label = n
        self.children = children

    def labels(self) -> Set[int]:
        """Return the set of all labels in the proof tree."""
        res = set([self.label])
        res.update(chain.from_iterable(node.labels() for node in self.children))
        return res

    def nodes(self) -> Iterator["Node"]:
        """Yield all nodes in the proof tree."""
        yield self
        for node in self.children:
            yield from node.nodes()

    def __str__(self) -> str:
        return "".join(["(", str(self.label), *map(str, self.children), ")"])

    def __len__(self) -> int:
        """Return the number nodes in the proof tree."""
        return 1 + sum(len(c) for c in self.children)


def prune(rdict: RulesDict) -> None:
    """
    Prune all nodes not in a combinatorial specification. This changes rdict
    in place.
    """
    changed = True
    while changed:
        changed = False
        for k, rule_set in list(rdict.items()):
            for rule in list(rule_set):
                if any(x not in rdict for x in rule):
                    rule_set.remove(rule)
                    changed = True
                if not rule_set:
                    del rdict[k]


def iterative_prune(rules_dict: RulesDict, root: Optional[int] = None) -> RulesDict:
    """Prune all nodes not iteratively verifiable."""
    verified_labels: Set[int] = set()
    if root is not None:
        verified_labels.add(root)
    rdict = deepcopy(rules_dict)
    new_rules_dict: RulesDict = defaultdict(set)
    while True:
        changed = False
        for k, rule_set in list(rdict.items()):
            for rule in list(rule_set):
                if all(x in verified_labels for x in rule):
                    changed = True
                    verified_labels.add(k)
                    new_rules_dict[k].add(rule)
                    rdict[k].remove(rule)
            if not rule_set:
                del rdict[k]
        if not changed:
            break
    return new_rules_dict


def proof_tree_dfs(rules_dict: RulesDict, root: int, seen: Optional[Set[int]] = None):
    """Return random proof tree found by depth first search."""
    if seen is None:
        seen = set()
    seen = seen.copy()
    if root in rules_dict:
        rule_set = rules_dict[root]
        root_node = Node(root)
        if root in seen or () in rule_set:
            seen.add(root)
            return seen, root_node
        seen.add(root)
        rule = choice(list(rule_set))
        visited, trees = all_proof_trees_dfs(rules_dict, rule, seen)
        root_node.children = trees
        return visited, root_node


def all_proof_trees_dfs(
    rules_dict: RulesDict, roots: Sequence[int], seen: Optional[Set[int]] = None
) -> Tuple[Set[int], List[Node]]:
    """Return all labels which have been seen, together with all of the trees
    using the given roots.."""
    if seen is None:
        seen = set()
    if not roots:
        return seen, []
    root, roots = roots[0], roots[1:]
    seen1, tree = proof_tree_dfs(rules_dict, root, seen)
    seen2, trees = all_proof_trees_dfs(rules_dict, roots, seen1)
    return seen1.union(seen2), [tree] + trees


def iterative_proof_tree_bfs(rules_dict: RulesDict, root: int) -> Node:
    """Takes in a iterative pruned rules_dict and returns iterative proof
    tree."""
    root_node = Node(root)
    queue = deque([root_node])
    while queue:
        v = queue.popleft()
        rule = sorted(rules_dict[v.label])[0]
        if not rule == ():
            children = [Node(i) for i in rule]
            queue.extend([child for child in children if not child.label == root])
            v.children = children
    return root_node


def random_proof_tree(rules_dict: RulesDict, root: int) -> Node:
    """Return random tree found by breadth first search."""
    seen: Set[int] = set()
    root_node = Node(root)
    queue = deque([root_node])
    while queue:
        v = queue.popleft()
        rule = choice(list(rules_dict[v.label]))
        if not (v.label in seen or rule == ()):
            children = [Node(i) for i in rule]
            shuffle(children)
            queue.extend(children)
            v.children = children
        seen.add(v.label)
    return root_node


def smallish_random_proof_tree(
    rules_dict: RulesDict, root: int, minimization_time_limit: float
) -> Node:
    """
    Searches a rule_dict known to contain at least one specification for a
    small specification. Spends minimization_time_limit seconds searching.
    """
    start_time = time.time()
    smallest_so_far = random_proof_tree(rules_dict, root=root)
    smallest_size = len(smallest_so_far)
    while time.time() - start_time < minimization_time_limit:
        next_tree = random_proof_tree(rules_dict, root=root)
        next_tree_size = len(next_tree)
        if next_tree_size < smallest_size:
            smallest_so_far = next_tree
            smallest_size = next_tree_size
    return smallest_so_far


def proof_tree_generator_bfs(rules_dict: RulesDict, root: int) -> Iterator[Node]:
    """A generator for all proof trees using breadth first search.
    N.B. The rules_dict is assumed to be pruned.
    """

    def _bfs_helper(root_label: int, seen: FrozenSet[int]):
        if root_label in seen:
            yield Node(root_label)
            return
        next_seen = seen.union((root_label,))
        for rule in rules_dict[root_label]:
            for children in product(
                *[_bfs_helper(child_label, next_seen) for child_label in rule]
            ):
                root_node = Node(root_label)
                root_node.children = children
                yield root_node

    sorted_rules_dict = {
        start: tuple(sorted(ends)) for start, ends in rules_dict.items()
    }

    if root in sorted_rules_dict:
        yield from _bfs_helper(root, frozenset())


def proof_tree_generator_dfs(
    rules_dict: RulesDict, root: int, maximum: Optional[int] = None
) -> Iterator[Node]:
    """A generator for all proof trees using depth first search.
    N.B. The rules_dict is assumed to be pruned.
    """

    def _dfs_tree(
        root_label: int, seen: FrozenSet[int], maximum: int = None
    ) -> Iterator[Tuple[FrozenSet[int], Node]]:
        if maximum is not None and maximum <= 0:
            return
        if root_label in seen:
            yield seen, Node(root_label)
            return
        seen = seen.union((root_label,))
        for rule in sorted_rules_dict[root_label]:
            if rule == ():
                yield seen, Node(root_label)
            else:
                for new_seen, children in _dfs_forest(rule, seen, maximum):
                    root_node = Node(root_label)
                    root_node.children = children
                    yield new_seen, root_node

    def _dfs_forest(
        root_labels: Sequence[int], seen: FrozenSet[int], maximum: Optional[int] = None
    ) -> Iterator[Tuple[FrozenSet[int], List[Node]]]:
        if maximum is not None and maximum <= 0:
            return
        if not root_labels:
            yield seen, []
        else:
            root, roots = root_labels[0], root_labels[1:]
            new_max = maximum - len(root_labels) + 1 if maximum is not None else None
            for seen1, tree in _dfs_tree(root, seen, new_max):
                length = len(tree)
                new_maximum = maximum - length if maximum is not None else None
                for seen2, trees in _dfs_forest(roots, seen1, new_maximum):
                    actual_length = length + sum(len(t) for t in trees)
                    if maximum is not None and actual_length < maximum:
                        yield seen1.union(seen2), [tree] + trees

    sorted_rules_dict = {
        start: tuple(sorted(ends)) for start, ends in rules_dict.items()
    }

    if root in sorted_rules_dict:
        for _, tree in _dfs_tree(root, frozenset(), maximum):
            yield tree


def iterative_proof_tree_finder(rules_dict: RulesDict, root: int) -> Node:
    """Finds an iterative proof tree for root, if one exists."""
    trees: Dict[int, Node] = {}

    def get_tree(start):
        if start == root:
            return Node(start)
        if start in trees:
            return trees[start]
        raise KeyError("{} is not in trees".format(start))

    def create_tree(start, end):
        if start in trees:
            return
        root = Node(start)
        children = [get_tree(i) for i in end]
        root.children = children
        trees[start] = root

    verified_labels = set()
    if root is not None:
        verified_labels.add(root)
    rdict = deepcopy(rules_dict)
    new_rules_dict: RulesDict = defaultdict(set)
    while True:
        changed = False
        for k, rule_set in list(rdict.items()):
            for rule in list(rule_set):
                if all(x in verified_labels for x in rule):
                    changed = True
                    verified_labels.add(k)
                    new_rules_dict[k].add(rule)
                    create_tree(k, rule)
                    rdict[k].remove(rule)
            if not rule_set:
                del rdict[k]
        if not changed:
            break
    if root in trees:
        return trees[root]
    raise ValueError("{} has no tree in rules_dict".format(root))
