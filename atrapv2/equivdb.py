'''
A database to keep track of equivalent tilings. This is done using a union find
method. Also, explanations of how tilings are equivalent are maintained.

Based on: https://www.ics.uci.edu/~eppstein/PADS/UnionFind.py
'''

class EquivalenceDB(object):
    '''
    A database for equivalences. Supports three methods.

    - DB[x] return a name for the set containing x. Each set named by
    arbitrarily chosen member.

    - DB.union(t1, t2, explanation) merges the sets containing t1 and t2 and
    records why t1 and t2 are equivalent.

    - DB.equivalent(t1, t2) returns True, if t1 and t2 are in the same set,
    otherwise returns False.
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
