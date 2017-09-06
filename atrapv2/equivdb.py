'''
A database to keep track of equivalent tilings. This is done using a union find
method. Also, explanations of how tilings are equivalent are maintained.

Based on: https://www.ics.uci.edu/~eppstein/PADS/UnionFind.py
'''

from collections import deque

class EquivalenceDB(object):
    '''
    A database for equivalences. Supports four methods.

    - DB[x] return a name for the set containing x. Each set named by
    arbitrarily chosen member.

    - DB.union(t1, t2, explanation) merges the sets containing t1 and t2 and
    records why t1 and t2 are equivalent.

    - DB.equivalent(t1, t2) returns True, if t1 and t2 are in the same set,
    otherwise returns False.

    - DB.get_relation(t1, t2) returns a string explaining why t1 and t2 are
      equivalent.

    '''
    def __init__(self):
        """Creates a new empty equivalent database."""
        self.parents = {}
        self.weights = {}
        self.explanations = {}
        self.verified_roots = set()

    def __getitem__(self, tiling):
        """Find and return root tiling for the set containing tiling."""
        root = self.parents.get(tiling)
        if root is None:
            self.parents[tiling] = tiling
            self.weights[tiling] = 1
            return tiling

        # Find path of tiling leading to root.
        path = [tiling]
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
        heaviest = max([(self.weights[r],r) for r in roots])[1]
        for r in roots:
            if r != heaviest:
                self.weights[heaviest] += self.weights[r]
                self.parents[r] = heaviest
        self.explanations[(t1,t2)] = explanation
        if (t2,t1) not in self.explanations:
            self.explanations[(t2,t1)] = "Reverse of: " + explanation

        self.update_verified(t1)


    def equivalent(self, t1, t2):
        return self[t1] == self[t2]

    def update_verified(self, tiling):
        if not self.is_verified(tiling):
            self.verified_roots.add(self[tiling])

    def is_verified(self, tiling):
        """Return true if any equivalent tiling is verified"""
        return self[tiling] in self.verified_roots

    def get_explanation(self, tiling, other_tiling):
        """Return how to tilings are equivalent using explanations."""
        if tiling == other_tiling:
            return ""

        path = self.find_path(tiling, other_tiling)
        if path:
            explanation = "| "
            for i in range(len(path) - 1):
                for j in range(i+1, len(path)):
                    t1 = path[i]
                    t2 = path[j]
                    key = (t1,t2)
                    if key in self.explanations:
                        explanation = explanation + self.explanations[key] + ". | "
                    key = (self[t2], self[t1])
                    if key in self.explanations:
                        explanation = explanation + "The reverse of: " + self.explanations[key] + ". | "
            return explanation
        '''We hopefully never get here'''
        return "they are on the same SiblingNode"

    def find_path(self, tiling, other_tiling):
        """
        BFS for shortest path.

        Used to find shortest explanation of why things are equivalent.
        """

        if not self.equivalent(tiling, other_tiling):
            raise KeyError("The tilings given are not equivalent.")
        equivalent_tilings = {}
        reverse_map = {}

        equivalent_label = self[tiling]

        for x in self.parents:
            n = len(equivalent_tilings)
            if self.equivalent(tiling, x):
                equivalent_tilings[x] = n
                reverse_map[n] = x

        adjacency_list = [[] for i in range(len(equivalent_tilings))]
        for (t1, t2) in self.explanations:
            if self.equivalent(t1, tiling):
                u = equivalent_tilings[t1]
                v = equivalent_tilings[t2]
                adjacency_list[u].append(v)
                adjacency_list[v].append(u)

        dequeue = deque()

        start = equivalent_tilings[tiling]
        end = equivalent_tilings[other_tiling]

        n = len(equivalent_tilings)

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
