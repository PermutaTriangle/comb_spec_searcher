"""
A database to keep track of equivalent objects.

This is done using a union find method. Also, explanations of how objects are
equivalent are maintained.

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

    def __getitem__(self, obj):
        """Find and return root object for the set containing object."""
        root = self.parents.get(obj)
        if root is None:
            self.parents[obj] = obj
            self.weights[obj] = 1
            return obj

        # Find path of object leading to root.
        path = [obj]
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

    def update_verified(self, obj):
        """Update database that objects euivalent to object are verified."""
        if not self.is_verified(obj):
            self.verified_roots.add(self[obj])

    def is_verified(self, obj):
        """Return true if any equivalent object is verified."""
        return self[obj] in self.verified_roots

    def equivalent_set(self, obj):
        equivalent_objs = set()
        for t in self.parents:
            if self.equivalent(obj, t):
                equivalent_objs.add(t)
        return equivalent_objs

    def get_explanation(self, obj, other_obj, one_step=False):
        """Return how two objects are equivalent using explanations."""
        if obj == other_obj:
            return ""

        if one_step:
            explanation = self.explanations.get((obj, other_obj))
            if explanation is None:
                explanation = self.explanations.get((other_obj, obj))
                assert explanation is not None
                explanation = "The reverse of: " + explanation
            return explanation

        path = self.find_path(obj, other_obj)
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

    def get_equiv_info(self, obj, other_obj):
        path = self.find_path(obj, other_obj)
        formal_step = self.get_explanation(obj, other_obj, path)



    def find_path(self, obj, other_obj):
        """
        BFS for shortest path.

        Used to find shortest explanation of why things are equivalent.
        """
        if not self.equivalent(obj, other_obj):
            raise KeyError("The objects given are not equivalent.")
        if obj == other_obj:
            return [obj]
        equivalent_objs = {}
        reverse_map = {}

        for x in self.parents:
            n = len(equivalent_objs)
            if self.equivalent(obj, x):
                equivalent_objs[x] = n
                reverse_map[n] = x

        adjacency_list = [[] for i in range(len(equivalent_objs))]
        for (t1, t2) in self.explanations:
            if self.equivalent(t1, obj):
                u = equivalent_objs[t1]
                v = equivalent_objs[t2]
                adjacency_list[u].append(v)
                adjacency_list[v].append(u)

        dequeue = deque()

        start = equivalent_objs[obj]
        end = equivalent_objs[other_obj]

        n = len(equivalent_objs)

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
