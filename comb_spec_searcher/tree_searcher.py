"""
Finds and returns a proof tree.
"""

__all__ = ("prune", "proof_tree_generator_dfs", "proof_tree_generator_bfs")

from random import choice, shuffle
from copy import deepcopy
from collections import defaultdict, deque

class Node(object):
    def __init__(self, n, children = []):
        self.label = n
        self.children = children
    def __str__(self):
        return "".join(["(", str(self.label), *map(str, self.children), ")"])

def prune(rules_dict):
    """Prune all unverifiable nodes (recursively)
    """
    rdict = deepcopy(rules_dict)
    changed = False
    for k, rule_set in list(rdict.items()):
        for rule in list(rule_set):
            if any(x not in rdict for x in rule):
                rule_set.remove(rule)
                changed = True
            if not rule_set:
                del rdict[k]
    return prune(rdict) if changed else rdict

def iterative_prune(rules_dict, root=None):
    verified_labels = set()
    if root is not None:
        verified_labels.add(root)
    rdict = deepcopy(rules_dict)
    new_rules_dict = defaultdict(set)
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

### DFS

def proof_tree_dfs(rules_dict, root, seen = set()):
    seen = seen.copy()
    if root in rules_dict:
        rule_set = rules_dict[root]
        root_node = Node(root)
        if root in seen or () in rule_set:
            seen.add(root)
            return seen, root_node
        else:
            seen.add(root)
            rule = choice(list(rule_set))
            visited, trees = proof_forest_dfs(rules_dict, rule, seen)
            root_node.children = trees
            return visited, root_node

def proof_forest_dfs(rules_dict, roots, seen = set()):
    if not roots:
        return seen, []
    else:
        root, roots = roots[0], roots[1:]
        seen1, tree = proof_tree_dfs(rules_dict, root, seen)
        seen2, trees = proof_forest_dfs(rules_dict, roots, seen1)
        return seen1.union(seen2), [tree] + trees

def proof_tree_generator_dfs(rules_dict, root):
    """A generator for random proof trees using depth first search.
    N.B. The rules_dict is assumed to be pruned.
    """
    while root in rules_dict:
        _, tree = proof_tree_dfs(rules_dict, root)
        yield tree


### BFS

def iterative_proof_tree_bfs(rules_dict, root):
    """Takes in a iterative_pruned rules_dict"""
    root_node = Node(root)
    queue = deque([root_node])
    while queue:
        v = queue.popleft()
        rule = sorted(rules_dict[v.label])[0]
        if not rule == ():
            children = [Node(i) for i in rule]
            queue.extend([child for child in children
                          if not child.label == root])
            v.children = children
    return root_node

def proof_tree_bfs(rules_dict, root):
    seen = set()
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
    return seen, root_node

def proof_tree_generator_bfs(rules_dict, root):
    """A generator for random proof trees using breadth first search.
    N.B. The rules_dict is assumed to be pruned.
    """
    while root in rules_dict:
        _, tree = proof_tree_bfs(rules_dict, root)
        yield tree
