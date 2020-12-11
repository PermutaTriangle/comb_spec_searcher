"""
A database to keep track of equivalent combinatorial classes.

This is done using a union find method. Also, explanations of how combinatorial
classes  are equivalent are maintained.

Based on: https://www.ics.uci.edu/~eppstein/PADS/UnionFind.py

In this file a combinatorial class is represented by a label, which is an
integer, that the classdb gives.
"""

from collections import defaultdict, deque
from typing import Deque, Dict, Iterator, Set, Tuple

from .utils import cssiteratortimer


class EquivalenceDB:
    """
    A database for equivalences. Supports four methods.

    - DB[x] return a name for the set containing x. Each set named by
    arbitrarily chosen member.
    - DB.union(t1, t2, explanation) merges the sets containing t1 and t2 and
    records why t1 and t2 are equivalent.
    - DB.equivalent(t1, t2) returns True, if t1 and t2 are in the same set,
    otherwise returns False.
    - DB.get_relation(t1, t2) returns a string explaining why t1 and t2 are
      equivalent.
    """

    def __init__(self) -> None:
        """Create a new empty equivalent database."""
        self.parents: Dict[int, int] = {}
        self.weights: Dict[int, int] = {}
        self.verified_roots: Set[int] = set()
        self.vertices: Dict[int, Set[int]] = defaultdict(set)
        self.func_times: Dict[str, float] = defaultdict(float)
        self.func_calls: Dict[str, int] = defaultdict(int)

    def __eq__(self, other: object) -> bool:
        """Check if all information stored is the same."""
        if not isinstance(other, EquivalenceDB):
            return NotImplemented
        return bool(
            self.parents == other.parents
            and self.weights == other.weights
            and self.verified_roots == other.verified_roots
            and self.vertices == other.vertices
        )

    def __getitem__(self, comb_class: int) -> int:
        """Find and return root combinatorial class for the set containing
        comb_class."""
        root = self.parents.get(comb_class)
        if root is None:
            self.parents[comb_class] = comb_class
            self.weights[comb_class] = 1
            return comb_class

        # Find path of combinatorial class leading to root.
        path = [comb_class]
        while root != path[-1]:
            path.append(root)
            root = self.parents[root]

        # Compress the path and return
        for ancestor in path:
            self.parents[ancestor] = root
        return root

    def add_edge(self, label: int, other_label: int) -> None:
        """Add an edge from label to other_label."""
        if label == other_label:
            return
        self.vertices[label].add(other_label)
        for path in self.find_paths(label, other_label):
            for x in path[:-1]:
                self._set_equivalent(x, label)

    @cssiteratortimer("find_paths")
    def find_paths(self, label: int, other_label: int) -> Iterator[Tuple[int, ...]]:
        """Return the list of path starting at other_label and ending at label."""
        dequeue: Deque[Tuple[int, ...]] = deque()
        dequeue.append((other_label,))
        while dequeue:
            path = dequeue.popleft()
            end = path[-1]
            if self.equivalent(end, label):
                yield path
                continue
            for new_end in self.vertices[end]:
                if new_end in path:
                    continue
                dequeue.append(path + (new_end,))

    def _set_equivalent(self, label: int, other_label: int) -> None:
        """Set the two labels as equivalent in UnionFind"""
        verified = self.is_verified(label) or self.is_verified(other_label)
        roots = [self[label], self[other_label]]
        heaviest = max([(self.weights[r], r) for r in roots])[1]
        for r in roots:
            if r != heaviest:
                self.weights[heaviest] += self.weights[r]
                self.parents[r] = heaviest
        if verified:
            self.set_verified(label)

    def equivalent(self, label: int, other_label: int) -> bool:
        """Return True if label and other_label are equivalent, False otherwise."""
        return self[label] == self[other_label]

    def set_verified(self, comb_class: int) -> None:
        """Update database that combinatorial classes equivalent to comb_class
        are verified."""
        if not self.is_verified(comb_class):
            self.verified_roots.add(self[comb_class])

    def is_verified(self, comb_class: int) -> bool:
        """Return true if any equivalent combinatorial class is verified."""
        return self[comb_class] in self.verified_roots

    def equivalent_set(self, comb_class: int) -> Set[int]:
        """Return all of the classes equivalent to comb_class."""
        equivalent_classes = set()
        for t in self.parents:
            if self.equivalent(comb_class, t):
                equivalent_classes.add(t)
        return equivalent_classes

    def find_path(self, comb_class: int, other_comb_class: int) -> Tuple[int, ...]:
        """
        BFS for shortest path.

        Used to find shortest explanation of why things are equivalent.
        """
        if not self.equivalent(comb_class, other_comb_class):
            raise KeyError("The classes given are not equivalent.")

        dequeue: Deque[Tuple[int, ...]] = deque()
        dequeue.append((comb_class,))
        visited: Set[int] = set()
        while dequeue:
            path = dequeue.popleft()
            end = path[-1]
            if end == other_comb_class:
                break
            if end in visited:
                continue
            for new_end in self.vertices[end]:
                if new_end in path:
                    continue
                dequeue.append(path + (new_end,))
            visited.add(path[-1])
        return path
