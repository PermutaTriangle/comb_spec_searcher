"""
  _______ __
 /_  __(_) /__ ___ _______  ___  ___
  / / / / / -_|_-</ __/ _ \/ _ \/ -_)
 /_/ /_/_/\__/___/\__/\___/ .__/\__/
                         /_/
"""

from collections import defaultdict, deque

class Node(object):
    def __init__(self, n, children = []):
        self.label = n
        self.children = children
    def __str__(self):
        return "".join(["(", str(self.label), *map(str, self.children), ")"])

def parse_table(text):
    rules_dict = defaultdict(set)
    rows = text.split('\n')
    root = int(rows[1])
    for row in rows[2:]:
        if row:
            fields = [ int(s) for s in row.split(' ') ]
            first, rest = fields[0], fields[1:]
            rules_dict[first] |= set((tuple(rest),))
    return rules_dict, root

def read_table(fname):
    return parse_table(open(fname).read())

def prune(rules_dict):
    """Prune all unverifiable nodes (recursively)
    """
    changed = False
    for k, rule_set in list(rules_dict.items()):
        for rule in list(rule_set):
            if any(x not in rules_dict for x in rule):
                rule_set.remove(rule)
                changed = True
            if not rule_set:
                del rules_dict[k]
    return prune(rules_dict) if changed else rules_dict

### DFS

def proof_trees_dfs(rules_dict, root, seen = set()):
    seen = seen.copy()
    if root in rules_dict:
        rule_set = rules_dict[root]
        root_node = Node(root)
        if root in seen or () in rule_set:
            seen.add(root)
            yield seen, root_node
        else:
            seen.add(root)
            for rule in rule_set:
                for visited, trees in proof_forests_dfs(rules_dict, rule, seen):
                    root_node.children = trees
                    yield visited, root_node

def proof_forests_dfs(rules_dict, roots, seen = set()):
    if not roots:
        yield seen, []
    else:
        root, roots = roots[0], roots[1:]
        for seen1, tree in proof_trees_dfs(rules_dict, root, seen):
            for seen2, trees in proof_forests_dfs(rules_dict, roots, seen1):
                yield seen1.union(seen2), [tree] + trees

def print_proof_trees_dfs(fname, n = 1):
    rules_dict, root = read_table(fname)
    try:
        gen = proof_trees_dfs(prune(rules_dict), root)
        for i in range(n):
            _, tree = next(gen)
            print(tree)
    except StopIteration:
        pass

### BFS

def disambiguate(rules_dict):
    if not rules_dict:
        yield dict()
    else:
        rdict = rules_dict.copy()
        v, rule_set = rdict.popitem()
        for rule in iter(rule_set):
            for d in disambiguate(rdict):
                d[v] = rule
                yield d

def proof_tree_bfs(unirules_dict, root):
    seen = set()
    root_node = Node(root)
    queue = deque([root_node])
    while queue:
        v = queue.popleft()
        rule = unirules_dict[v.label]
        if not (v.label in seen or rule == ()):
            children = [ Node(i) for i in rule ]
            queue.extend(children)
            v.children = children
        seen.add(v.label)
    return seen, root_node

def proof_trees_bfs(rules_dict, root):
    rdict = prune(rules_dict)
    if root in rdict:
        for d in disambiguate(rdict):
            yield proof_tree_bfs(d, root)

def print_proof_trees_bfs(gen, n = 1):
    try:
        for i in range(n):
            _, tree = next(gen)
            print(tree)
    except StopIteration:
        pass
