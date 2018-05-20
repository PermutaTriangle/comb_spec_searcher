"""
A database to keep track of equivalent combinatorial classes.

This is done using a union find method. Also, explanations of how combinatorial
classes  are equivalent are maintained.

Based on: https://www.ics.uci.edu/~eppstein/PADS/UnionFind.py
"""

from collections import deque


class EquivalenceDB(object):
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

    def __init__(self):
        """Create a new empty equivalent database."""
        self.parents = {}
        self.weights = {}
        self.explanations = {}
        self.verified_roots = set()

    def to_dict(self):
        """Return dictionary object of self that is JSON serializable."""
        return {
            'parents': self.parents,
            'weights': self.weights,
            'explanations': [(list(x), y)
                             for x, y in self.explanations.items()],
            'verified_roots': list(self.verified_roots),
        }

    @classmethod
    def from_dict(cls, dict):
        """Return EquivalenceDB object for dictionary object."""
        equivdb = cls()
        equivdb.parents = dict['parents']
        equivdb.weights = dict['weights']
        equivdb.explanations = {tuple(x): y
                                for x, y in dict['explanations']}
        equivdb.verified_roots = set(dict['verified_roots'])
        return equivdb

    def __getitem__(self, comb_class):
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

    def union(self, t1, t2, explanation):
        """Find sets containing t1 and t2 and merge them."""
        verified = self.is_verified(t1) or self.is_verified(t2)
        roots = [self[t1], self[t2]]
        heaviest = max([(self.weights[r], r) for r in roots])[1]
        for r in roots:
            if r != heaviest:
                self.weights[heaviest] += self.weights[r]
                self.parents[r] = heaviest
        self.explanations[(t1, t2)] = explanation
        if (t2, t1) not in self.explanations:
            self.explanations[(t2, t1)] = "Reverse of: " + explanation
        if verified:
            self.update_verified(t1)

    def equivalent(self, t1, t2):
        """Return True if t1 and t2 are equivalent, False otherwise."""
        return self[t1] == self[t2]

    def update_verified(self, comb_class):
        """Update database that combinatorial classes equivalent to comb_class
        are verified."""
        if not self.is_verified(comb_class):
            self.verified_roots.add(self[comb_class])

    def is_verified(self, comb_class):
        """Return true if any equivalent combinatorial class is verified."""
        return self[comb_class] in self.verified_roots

    def equivalent_set(self, comb_class):
        equivalent_classes = set()
        for t in self.parents:
            if self.equivalent(comb_class, t):
                equivalent_classes.add(t)
        return equivalent_classes

    def get_explanation(self, comb_class, other_comb_class, one_step=False):
        """Return how two combinatorial classes are equivalent using
        explanations."""
        if comb_class == other_comb_class:
            return ""

        if one_step:
            explanation = self.explanations.get((comb_class, other_comb_class))
            if explanation is None:
                explanation = self.explanations.get((other_comb_class,
                                                     comb_class))
                assert explanation is not None
                explanation = "The reverse of: " + explanation
            return explanation

        path = self.find_path(comb_class, other_comb_class)
        if path:
            explanation = "| "
            for i in range(len(path) - 1):
                for j in range(i+1, len(path)):
                    t1 = path[i]
                    t2 = path[j]
                    key = (t1, t2)
                    if key in self.explanations:
                        new_explanation = self.explanations[key]
                        explanation = explanation + new_explanation + ". | "
                    key = (self[t2], self[t1])
                    if key in self.explanations:
                        new_explanation = self.explanations[key]
                        new_explanation = "The reverse of: " + new_explanation
                        explanation = explanation + new_explanation + ". | "
            return explanation
        raise KeyError("They are not equivalent.")

    def get_equiv_info(self, comb_class, other_comb_class):
        path = self.find_path(comb_class, other_comb_class)
        formal_step = self.get_explanation(comb_class, other_comb_class, path)

    def find_path(self, comb_class, other_comb_class):
        """
        BFS for shortest path.

        Used to find shortest explanation of why things are equivalent.
        """
        if not self.equivalent(comb_class, other_comb_class):
            raise KeyError("The classes given are not equivalent.")
        if comb_class == other_comb_class:
            return [comb_class]
        equivalent_comb_classes = {}
        reverse_map = {}

        for x in self.parents:
            n = len(equivalent_comb_classes)
            if self.equivalent(comb_class, x):
                equivalent_comb_classes[x] = n
                reverse_map[n] = x

        adjacency_list = [[] for i in range(len(equivalent_comb_classes))]
        for (t1, t2) in self.explanations:
            if self.equivalent(t1, comb_class):
                u = equivalent_comb_classes[t1]
                v = equivalent_comb_classes[t2]
                adjacency_list[u].append(v)
                adjacency_list[v].append(u)

        dequeue = deque()

        start = equivalent_comb_classes[comb_class]
        end = equivalent_comb_classes[other_comb_class]

        n = len(equivalent_comb_classes)

        dequeue.append(start)
        visited = [False for i in range(n)]
        neighbour = [None for i in range(n)]
        while len(dequeue) > 0:
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
            t = reverse_map[neighbour[end]]
            path.append(t)
            end = neighbour[end]

        return path[::-1]
