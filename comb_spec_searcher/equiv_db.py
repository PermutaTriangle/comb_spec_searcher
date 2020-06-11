"""
A database to keep track of equivalent combinatorial classes.

This is done using a union find method. Also, explanations of how combinatorial
classes  are equivalent are maintained.

Based on: https://www.ics.uci.edu/~eppstein/PADS/UnionFind.py

In this file a combinatorial class is represented by a label, which is an
integer, that the classdb gives.
"""

from collections import deque
from typing import Deque, Dict, FrozenSet, List, Set, Union


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
        self.vertices: Set[FrozenSet[int]] = set()

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

    def union(self, t1: int, t2: int) -> None:
        """Find sets containing t1 and t2 and merge them."""
        if t1 == t2:
            return
        self.vertices.add(frozenset((t1, t2)))
        verified = self.is_verified(t1) or self.is_verified(t2)
        roots = [self[t1], self[t2]]
        heaviest = max([(self.weights[r], r) for r in roots])[1]
        for r in roots:
            if r != heaviest:
                self.weights[heaviest] += self.weights[r]
                self.parents[r] = heaviest
        if verified:
            self.set_verified(t1)

    def equivalent(self, t1: int, t2: int) -> bool:
        """Return True if t1 and t2 are equivalent, False otherwise."""
        return self[t1] == self[t2]

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

    def find_path(self, comb_class: int, other_comb_class: int) -> List[int]:
        """
        BFS for shortest path.

        Used to find shortest explanation of why things are equivalent.
        """
        if not self.equivalent(comb_class, other_comb_class):
            raise KeyError("The classes given are not equivalent.")
        if comb_class == other_comb_class:
            return [comb_class]
        equivalent_comb_classes: Dict[int, int] = {}
        reverse_map: Dict[int, int] = {}

        for x in self.parents:
            n = len(equivalent_comb_classes)
            if self.equivalent(comb_class, x):
                equivalent_comb_classes[x] = n
                reverse_map[n] = x

        adjacency_list: List[List[int]] = [
            [] for i in range(len(equivalent_comb_classes))
        ]
        for (t1, t2) in self.vertices:
            if self.equivalent(t1, comb_class):
                u = equivalent_comb_classes[t1]
                v = equivalent_comb_classes[t2]
                adjacency_list[u].append(v)
                adjacency_list[v].append(u)

        dequeue: Deque[int] = deque()

        start = equivalent_comb_classes[comb_class]
        end = equivalent_comb_classes[other_comb_class]

        n = len(equivalent_comb_classes)

        dequeue.append(start)
        visited = [False for i in range(n)]
        neighbour: List[Union[int, None]] = [None for i in range(n)]
        while dequeue:
            u = dequeue.popleft()
            if u == end:
                break
            if visited[u]:
                continue
            visited[u] = True

            for v in adjacency_list[u]:
                if not visited[v]:
                    dequeue.append(v)
                    neighbour[v] = u

        path = [reverse_map[end]]
        while neighbour[end] is not None:
            assert isinstance(end, int), "something went wrong"
            a = neighbour[end]
            assert isinstance(a, int), "something went wrong"
            t = reverse_map[a]
            path.append(t)
            end = a

        return path[::-1]
