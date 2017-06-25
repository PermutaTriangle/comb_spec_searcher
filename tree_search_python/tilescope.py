"""
  _______ __
 /_  __(_) /__ ___ _______  ___  ___
  / / / / / -_|_-</ __/ _ \/ _ \/ -_)
 /_/ /_/_/\__/___/\__/\___/ .__/\__/
                         /_/
"""

from collections import defaultdict

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
    return root, rules_dict

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

def proof_trees_dfs(root, rules_dict, seen = set()):
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
                for visited, trees in proof_forests_dfs(rule, rules_dict, seen):
                    root_node.children = trees
                    yield visited, root_node

def proof_forests_dfs(roots, rules_dict, seen = set()):
    if not roots:
        yield seen, []
    else:
        root, roots = roots[0], roots[1:]
        for seen1, tree in proof_trees_dfs(root, rules_dict, seen):
            for seen2, trees in proof_forests_dfs(roots, rules_dict, seen1):
                yield seen1.union(seen2), [tree] + trees

def print_proof_tree_dfs(fname, n = 1):
    root, rules_dict = read_table(fname)
    try:
        gen = proof_trees_dfs(root, prune(rules_dict))
        for i in range(n):
            _, tree = next(gen)
            print(tree)
    except StopIteration:
        print("No proof tree found")
