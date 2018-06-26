"""
A proof tree class.

This can be used to get the generating function for the class.
"""
import json
import sys
import sympy
from functools import reduce
from operator import add, mul

from permuta.misc.ordered_set_partitions import partitions_of_n_of_size_k

from .tree_searcher import Node as tree_searcher_node


class ProofTreeNode(object):
    def __init__(self, label, eqv_path_labels, eqv_path_objects,
                 eqv_explanations=[], children=[], strategy_verified=False,
                 decomposition=False, disjoint_union=False, recursion=False,
                 formal_step=""):
        self.label = label
        self.eqv_path_labels = eqv_path_labels
        self.eqv_path_objects = eqv_path_objects
        self.eqv_explanations = eqv_explanations
        self.children = children
        self.strategy_verified = strategy_verified
        self.decomposition = decomposition
        self.disjoint_union = disjoint_union
        self.recursion = recursion
        # TODO: Add assertions for assumptions made about each type of strategy
        self.formal_step = formal_step
        self.sympy_function = None

    def to_jsonable(self):
        output = dict()
        output['label'] = self.label
        output['eqv_path_labels'] = [x for x in self.eqv_path_labels]
        output['eqv_path_objects'] = [x.to_jsonable()
                                      for x in self.eqv_path_objects]
        output['eqv_explanations'] = [x for x in self.eqv_explanations]
        output['children'] = [child.to_jsonable() for child in self.children]
        output['strategy_verified'] = self.strategy_verified
        output['decomposition'] = self.decomposition
        output['disjoint_union'] = self.disjoint_union
        output['recursion'] = self.recursion
        output['formal_step'] = self.formal_step
        return output

    @classmethod
    def from_dict(cls, combclass, jsondict):
        return cls(label=jsondict['label'],
                   eqv_path_labels=jsondict['eqv_path_labels'],
                   eqv_path_objects=[combclass.from_dict(x)
                                     for x in jsondict['eqv_path_objects']],
                   eqv_explanations=jsondict['eqv_explanations'],
                   children=[ProofTreeNode.from_dict(combclass, child)
                             for child in jsondict['children']],
                   strategy_verified=jsondict['strategy_verified'],
                   decomposition=jsondict['decomposition'],
                   disjoint_union=jsondict['disjoint_union'],
                   recursion=jsondict['recursion'],
                   formal_step=jsondict['formal_step'])

    @classmethod
    def from_json(cls, combclass, jsonstr):
        jsondict = json.loads(jsonstr)
        return cls.from_dict(combclass, jsondict)

    def _error_string(self, parent, children, strat_type, formal_step,
                      length, parent_total, children_total):
        error = "Insane " + strat_type + " Strategy Found!\n"
        error += formal_step + "\n"
        error += "Found at length {} \n".format(length)
        error += "The parent object was:\n{}\n".format(parent.__repr__())
        error += "It produced {} many things\n".format(parent_total)
        error += "The children were:\n"
        for obj in children:
            error += obj.__repr__()
            error += "\n"
        error += "They produced {} many things\n\n".format(children_total)
        return error

    def sanity_check(self, length, of_length=None):
        if of_length is None:
            raise ValueError("of_length is undefined.")

        number_objs = of_length(self.eqv_path_objects[0], length)
        for i, obj in enumerate(self.eqv_path_objects[1:]):
            eqv_number = of_length(obj, length)
            if number_objs != eqv_number:
                formal_step = ""
                for i in range(i+1):
                    formal_step += self.eqv_explanations[i]
                return self._error_string(self.eqv_path_objects[0],
                                          [obj],
                                          "Equivalent",
                                          formal_step,
                                          length,
                                          number_objs,
                                          eqv_number)
        if self.disjoint_union:
            child_objs = [child.eqv_path_objects[0] for child in self.children]
            total = 0
            for obj in child_objs:
                total += of_length(obj, length)
            if number_objs != total:
                return self._error_string(self.eqv_path_objects[0],
                                          child_objs,
                                          "Batch",
                                          self.formal_step,
                                          length,
                                          number_objs,
                                          total)
        if self.decomposition:
            child_objs = [child.eqv_path_objects[0]
                          for child in self.children]
            total = 0
            for part in partitions_of_n_of_size_k(length, len(child_objs)):
                subtotal = 1
                for obj, partlen in zip(child_objs, part):
                    if subtotal == 0:
                        break
                    subtotal *= of_length(obj, partlen)
                total += subtotal
            if number_objs != total:
                return self._error_string(self.eqv_path_objects[0],
                                          child_objs,
                                          "Decomposition",
                                          self.formal_step,
                                          length,
                                          number_objs,
                                          total)

    def __eq__(self, other):
        return all([self.label == other.label,
                    self.eqv_path_labels == other.eqv_path_labels,
                    self.eqv_path_objects == other.eqv_path_objects,
                    self.eqv_explanations == other.eqv_explanations,
                    self.children == other.children,
                    self.strategy_verified == other.strategy_verified,
                    self.decomposition == other.decomposition,
                    self.disjoint_union == other.disjoint_union,
                    self.recursion == other.recursion,
                    self.formal_step == other.formal_step])

    def get_function(self):
        if self.sympy_function is None:
            self.sympy_function = sympy.Function("F_" +
                                                 str(self.label))(sympy.abc.x)
        return self.sympy_function

    def get_equation(self, root_func=None, root_class=None,
                     substitutions=False):
        lhs = self.get_function()
        if self.disjoint_union:
            rhs = reduce(add,
                         [child.get_function() for child in self.children],
                         0)
        elif self.decomposition:
            rhs = reduce(mul,
                         [child.get_function() for child in self.children],
                         1)
        elif self.recursion:
            rhs = lhs
        elif self.strategy_verified:
            rhs = self.eqv_path_objects[-1].get_genf(root_func=root_func,
                                                     root_class=root_class)
        else:
            raise NotImplementedError("Using an unimplemented constructor")
        return sympy.Eq(lhs, rhs)


class InsaneTreeError(Exception):
    pass


class ProofTree(object):
    def __init__(self, root):
        if not isinstance(root, ProofTreeNode):
            raise TypeError("Root must be a ProofTreeNode.")
        self.root = root
        self._of_length_cache = {}

    def to_jsonable(self):
        return {'root': self.root.to_jsonable()}

    @classmethod
    def from_dict(cls, combclass, jsondict):
        root = ProofTreeNode.from_dict(combclass, jsondict['root'])
        return cls(root)

    @classmethod
    def from_json(cls, combclass, jsonstr):
        jsondict = json.loads(jsonstr)
        return cls.from_dict(combclass, jsondict)

    def _of_length(self, obj, length):
        if obj not in self._of_length_cache:
            self._of_length_cache[obj] = {}

        number = self._of_length_cache[obj].get(length)

        if number is None:
            number = len(list(obj.objects_of_length(length)))
            self._of_length_cache[obj][length] = number

        return number

    def print_equivalences(self):
        for node in self.nodes():
            print("===============")
            print(node.label)
            for o in node.eqv_path_objects:
                print(o.__repr__())
                print()

    def get_equations(self):
        eqs = set()
        subs = {}
        root_func = self.root.get_function()
        root_class = self.root.eqv_path_objects[0]
        for node in self.nodes():
            if node.recursion:
                continue
            eqs.add(node.get_equation(substitutions=True,
                                      root_func=root_func,
                                      root_class=root_class))
        return eqs

    def get_genf(self, verbose=False, verify=8):
        """Find generating function for proof tree. Return None if no solution
        is found. If not verify will return list of possible solutions."""
        # TODO: add substitutions, so as to solve with symbols first.
        eqs = self.get_equations()
        root_class = self.root.eqv_path_objects[0]
        root_func = self.root.get_function()
        if verbose:
            print("The system of", len(eqs), "equations:")
            for eq in eqs:
                print(eq.lhs, "=", eq.rhs)
            print()
            print("Solving...")
        solutions = sympy.solve(eqs, tuple([eq.lhs for eq in eqs]), dict=True,
                                cubics=False, quartics=False, quintics=False)
        if solutions:
            if not verify:
                return solutions
            if verbose and verify:
                print("Solved, verifying solutions.")
            objcounts = [len(list(root_class.objects_of_length(i)))
                         for i in range(verify + 1)]
            for solution in solutions:
                genf = solution[root_func]
                try:
                    expansion = taylor_expand(genf, verify)
                except Exception as e:
                    # print(e)
                    continue
                if objcounts == expansion:
                    return genf
        if solutions:
            raise RuntimeError(("Incorrect generating function\n" +
                                str(solutions)))

    def nodes(self, root=None):
        if root is None:
            root = self.root
        yield root
        for child in root.children:
            for node in self.nodes(root=child):
                yield node

    def number_of_nodes(self):
        return len(list(self.nodes()))

    def number_of_objects(self):
        count = 0
        for node in self.nodes():
            count += len(node.eqv_path_objects)
        return count

    def sanity_check(self, length=8, raiseerror=True):
        overall_error = ""
        for node in self.nodes():
            error = node.sanity_check(length, self._of_length)
            if error is not None:
                if raiseerror:
                    raise InsaneTreeError(error)
                else:
                    overall_error += error
        if overall_error:
            return False, overall_error
        else:
            return True, "Sanity checked, all good at length {}".format(length)

    @classmethod
    def from_comb_spec_searcher(cls, root, css):
        if not isinstance(root, tree_searcher_node):
            raise TypeError("Requires a tree searcher node, treated as root.")
        proof_tree = ProofTree(ProofTree.from_comb_spec_searcher_node(root,
                                                                      css))
        proof_tree._recursion_fixer(css)
        return proof_tree

    def _recursion_fixer(self, css, root=None, in_labels=None):
        if root is None:
            root = self.root
        if in_labels is None:
            in_labels = list(self.non_recursive_in_labels())
        if root.recursion:
            in_label = root.eqv_path_labels[0]
            out_label = in_label
            for eqv_label in in_labels:
                if css.equivdb.equivalent(in_label, eqv_label):
                    out_label = eqv_label
                    break
            assert css.equivdb.equivalent(in_label, out_label)

            eqv_path = css.equivdb.find_path(in_label, out_label)
            eqv_objs = [css.classdb.get_class(l) for l in eqv_path]
            eqv_explanations = [css.equivdb.get_explanation(x, y,
                                                            one_step=True)
                                for x, y in zip(eqv_path[:-1], eqv_path[1:])]

            root.eqv_path_labels = eqv_path
            root.eqv_path_objects = eqv_objs
            root.eqv_explanations = eqv_explanations

        for child in root.children:
            self._recursion_fixer(css, child, in_labels)

    def non_recursive_in_labels(self, root=None):
        if root is None:
            root = self.root
        if not root.recursion:
            yield root.eqv_path_labels[0]
        for child in root.children:
            for x in self.non_recursive_in_labels(child):
                yield x

    @classmethod
    def from_comb_spec_searcher_node(cls, root, css, in_label=None):
        if not isinstance(root, tree_searcher_node):
            raise TypeError("Requires a tree searcher node, treated as root.")
        label = root.label
        if in_label is None:
            in_label = root.label
        else:
            assert css.equivdb.equivalent(root.label, in_label)
        children = root.children

        if not children:
            eqv_ver_label = css.equivalent_strategy_verified_label(in_label)
            if eqv_ver_label is not None:
                # verified!
                eqv_path = css.equivdb.find_path(in_label, eqv_ver_label)
                eqv_objs = [css.classdb.get_class(l) for l in eqv_path]
                eqv_explanations = [css.equivdb.get_explanation(x, y,
                                                                one_step=True)
                                    for x, y in zip(eqv_path[:-1],
                                                    eqv_path[1:])]

                formal_step = css.classdb.verification_reason(eqv_ver_label)
                return ProofTreeNode(label, eqv_path, eqv_objs,
                                     eqv_explanations, strategy_verified=True,
                                     formal_step=formal_step)
            else:
                # recurse! we reparse these at the end, so recursed labels etc
                # are not interesting.
                return ProofTreeNode(label, [in_label],
                                     [css.classdb.get_class(in_label)],
                                     formal_step="recurse",
                                     recursion=True)
        else:
            rule = css.rule_from_equivence_rule(root.label,
                                                tuple(c.label
                                                      for c in root.children))
            start, ends = rule
            formal_step = css.ruledb.explanation(start, ends)
            constructor = css.ruledb.constructor(start, ends)

            eqv_path = css.equivdb.find_path(in_label, start)
            eqv_objs = [css.classdb.get_class(l) for l in eqv_path]
            eqv_explanations = [css.equivdb.get_explanation(x, y,
                                                            one_step=True)
                                for x, y in zip(eqv_path[:-1], eqv_path[1:])]

            strat_children = []
            for next_label in ends:
                for child in root.children:
                    if css.equivdb.equivalent(next_label, child.label):
                        sub_tree = ProofTree.from_comb_spec_searcher_node(
                                                        child, css, next_label)
                        strat_children.append(sub_tree)
                        break
            if constructor == 'cartesian':
                # decomposition!
                return ProofTreeNode(label, eqv_path, eqv_objs,
                                     eqv_explanations, decomposition=True,
                                     formal_step=formal_step,
                                     children=strat_children)
            elif constructor == 'disjoint' or constructor == 'equiv':
                # batch!
                return ProofTreeNode(label, eqv_path, eqv_objs,
                                     eqv_explanations, disjoint_union=True,
                                     formal_step=formal_step,
                                     children=strat_children)
            else:
                print(constructor, type(constructor))
                raise NotImplementedError("Only handle cartesian and disjoint")

    def __eq__(self, other):
        return all(node1 == node2
                   for node1, node2 in zip(self.nodes(), other.nodes()))


def taylor_expand(genf, n=10):
    num, den = genf.as_numer_denom()
    num = num.expand()
    den = den.expand()
    genf = num/den
    ser = sympy.Poly(genf.series(n=n+1).removeO(), sympy.abc.x)
    res = ser.all_coeffs()
    res = res[::-1] + [0]*(n+1-len(res))
    return res
