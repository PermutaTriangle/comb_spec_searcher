"""
A proof tree class.

This has been built specific to tilings and gridded perms. Needs to be
generalised.
"""

from grids_two import Tiling

from .tree_searcher import Node as tree_searcher_node
from permuta.misc.ordered_set_partitions import partitions_of_n_of_size_k

from functools import reduce
from operator import add, mul

import sys

import json


class ProofTreeNode(object):
    def __init__(self, label, eqv_path_labels, eqv_path_objects,
                 eqv_explanations=[], children=[], strategy_verified=False,
                 complement_verified=False, decomposition=False,
                 disjoint_union=False, recursion=False, formal_step="",
                 back_maps=None, forward_maps=None):
        self.label = label
        self.eqv_path_labels = eqv_path_labels
        self.eqv_path_objects = eqv_path_objects
        self.eqv_explanations = eqv_explanations

        self.children = children
        self.strategy_verified = strategy_verified
        self.complement_verified = complement_verified
        self.decomposition = decomposition
        self.disjoint_union = disjoint_union
        self.recursion = recursion
        # TODO: Add assertions for assumptions made about each type of strategy.
        self.formal_step = formal_step
        self.back_maps = back_maps
        self.forward_maps = forward_maps

    def to_jsonable(self):
        output = dict()
        output['label'] = self.label
        output['eqv_path_labels'] = [x for x in self.eqv_path_labels]
        output['eqv_path_objects'] = [x.to_jsonable()
                                      for x in self.eqv_path_objects]
        output['eqv_explanations'] = [x for x in self.eqv_explanations]
        output['children'] = [child.to_jsonable() for child in self.children]
        output['strategy_verified'] = self.strategy_verified
        output['complement_verified'] = self.complement_verified
        output['decomposition'] = self.decomposition
        output['disjoint_union'] = self.disjoint_union
        output['recursion'] = self.recursion
        output['formal_step'] = self.formal_step
        if self.back_maps is not None:
            output['back_maps'] = [[(x, y) for x, y in bm.items()]
                                 for bm in self.back_maps]
        if self.forward_maps is not None:
            output['forward_maps'] = [fm for fm in self.forward_maps]
        return output

    @classmethod
    def from_dict(cls, jsondict):
        from grids_two import Tiling
        back_maps = jsondict.get('back_maps')
        if back_maps is not None:
            back_maps = [{tuple(x): tuple(y) for x, y in bm}
                         for bm in back_maps]
        forward_maps = jsondict.get('forward_maps')
        if forward_maps is not None:
            raise NotImplementedError('Fix forward maps in jsoning!!!')
        return cls(label=jsondict['label'],
                   eqv_path_labels=jsondict['eqv_path_labels'],
                   eqv_path_objects=[Tiling.from_dict(x)
                                     for x in jsondict['eqv_path_objects']],
                   eqv_explanations=jsondict['eqv_explanations'],
                   children=[ProofTreeNode.from_dict(child)
                             for child in jsondict['children']],
                   strategy_verified=jsondict['strategy_verified'],
                   complement_verified=jsondict['complement_verified'],
                   decomposition=jsondict['decomposition'],
                   disjoint_union=jsondict['disjoint_union'],
                   recursion=jsondict['recursion'],
                   formal_step=jsondict['formal_step'],
                   back_maps=back_maps,
                   forward_maps=forward_maps)

    @classmethod
    def from_json(cls, jsonstr):
        jsondict = json.loads(jsonstr)
        return cls.from_dict(jsondict)

    def _error_string(self, parent, children, strat_type,
                      length, parent_total, children_total):
        error = "Insane " + strat_type + " Strategy Found!\n"
        error += "Found at length {} \n".format(length)
        error += "The parent tiling was:\n{}\n".format(parent.__repr__())
        error += "It produced {} many things\n".format(length)
        error += "The children were:\n"
        for obj in children:
            error += obj.__repr__()
            error += "\n"
        error += "They produced {} many things\n\n".format(children_total)
        return error


    def sanity_check(self, length, of_length=None):
        if of_length is None:
            raise ValueError("of_length is undefined.")
        if self.complement_verified:
            return ("Don't use complement_verified, its dangerous.")

        number_perms = of_length(self.eqv_path_objects[0], length)
        for obj in self.eqv_path_objects[1:]:
            eqv_number = of_length(obj, length)
            if number_perms != eqv_number:
                return self._error_string(self.eqv_path_objects[0],
                                          [obj],
                                          "Equivalent",
                                          length,
                                          number_perms,
                                          eqv_number)
        if self.disjoint_union:
            child_objs = [child.eqv_path_objects[0] for child in self.children]
            total = 0
            for obj in child_objs:
                total += of_length(obj, length)
            if number_perms != total:
                return self._error_string(self.eqv_path_objects[0],
                                          child_objs,
                                          "Batch",
                                          length,
                                          number_perms,
                                          total)
        if self.decomposition:
            if not self.has_interleaving_decomposition():
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
                if number_perms != total:
                    return self._error_string(self.eqv_path_objects[0],
                                              child_objs,
                                              "Decomposition",
                                              length,
                                              number_perms,
                                              total)

    def has_interleaving_decomposition(self):
        if self.back_maps is None:
            return False
        mixing = False
        bmps1 = [{c[0] for c in dic.values()} for dic in self.back_maps]
        bmps2 = [{c[1] for c in dic.values()} for dic in self.back_maps]
        for i in range(len(self.back_maps)):
            for j in range(len(self.back_maps)):
                if i != j:
                    if (bmps1[i] & bmps1[j]) or (bmps2[i] & bmps2[j]):
                        mixing = True
        if mixing:
            return True
        return False

    def __eq__(self, other):
        return all([self.label == other.label,
                    self.eqv_path_labels == other.eqv_path_labels,
                    self.eqv_path_objects == other.eqv_path_objects,
                    self.eqv_explanations == other.eqv_explanations,
                    self.children == other.children,
                    self.strategy_verified == other.strategy_verified,
                    self.complement_verified == other.complement_verified,
                    self.decomposition == other.decomposition,
                    self.disjoint_union == other.disjoint_union,
                    self.recursion == other.recursion,
                    self.formal_step == other.formal_step,
                    self.back_maps == other.back_maps,
                    self.forward_maps == other.forward_maps])


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

    def to_json(self):
        from .old_proof_tree import ProofTree as OldProofTree
        old_proof_tree = OldProofTree(self._to_old_proof_tree_node(self.root))
        return old_proof_tree.to_json()

    @classmethod
    def from_dict(cls, jsondict):
        root = ProofTreeNode.from_dict(jsondict['root'])
        return cls(root)

    @classmethod
    def from_json(cls, jsonstr):
        jsondict = json.loads(jsonstr)
        return cls.from_dict(jsondict)

    def _of_length(self, obj, length):
        if obj not in self._of_length_cache:
            self._of_length_cache[obj] = {}

        number = self._of_length_cache[obj].get(length)

        if number is None:
            number = len(list(obj.gridded_perms_of_length(length)))
            self._of_length_cache[obj][length] = number

        return number

    def print_equivalences(self):
        for node in self.nodes():
            print("===============")
            print(node.label)
            for o in node.eqv_path_objects:
                print(o.__repr__())
                print()

    def to_old_proof_tree(self):
        from .old_proof_tree import ProofTree as OldProofTree
        old_proof_tree = OldProofTree(self._to_old_proof_tree_node(self.root))
        return old_proof_tree

    def _to_old_proof_tree_node(self, root):
        from .old_proof_tree import ProofTreeNode as OldProofTreeNode
        relation = ""
        for x in root.eqv_explanations:
            relation = relation + x
        if root.back_maps:
            from grids import Cell
            recurse = [{Cell(*key): Cell(*val) for key, val in bm.items()}
                       for bm in root.back_maps]
        else:
            recurse = None
        return OldProofTreeNode(root.formal_step,
                                root.eqv_path_objects[0].to_old_tiling(),
                                root.eqv_path_objects[-1].to_old_tiling(),
                                relation,
                                root.label,
                                children=[self._to_old_proof_tree_node(x)
                                          for x in root.children],
                                recurse=recurse,
                                strategy_verified=root.strategy_verified)

    def pretty_print(self, file=sys.stderr):
        """Pretty print using olf proof tree class."""
        self.to_old_proof_tree().pretty_print(file=file)
    
    def get_funcs(self):
        """Creates a dictionary mapping from labels to function names"""
        funcs = {}
        self._get_funcs(self.root, funcs)
        return funcs

    def _get_funcs(self, root, funcs):
        from sympy import Function
        if root.label not in funcs:
            funcs[root.label] = Function("F_"+str(root.label))
        for child in root.children:
            self._get_funcs(child, funcs)
    
    def get_equations(self, me, funcs, substitutions=None, fcache=None):
        res = None
        f = False # should we substitute before returning?
        if substitutions == None:
            substitutions = {}
            fcache = {}
            f = True
        res = self._get_equations(self.root, me, funcs, substitutions, fcache)
        if f:
            res = [v.subs(substitutions) for v in res]
        return sorted(set(res), key = lambda x: int(str(x.lhs)[2:-3]))

    def _get_equations(self, root, me, funcs, substitutions, fcache):
        #from atrap.Helpers import get_tiling_genf
        from sympy import Eq
        from sympy.abc import x
        lhs = funcs[root.label](x)
        rhs = 0
        assert(root.decomposition + root.disjoint_union + root.complement_verified + root.strategy_verified + root.recursion == 1)
        if root.decomposition:
            assert(len(root.children) > 0)
            rhs = reduce(mul, [funcs[child.label](x) for child in root.children], 1)
        elif root.disjoint_union:
            assert(len(root.children) > 0)
            rhs = reduce(add, [funcs[child.label](x) for child in root.children], 0)
        elif root.complement_verified:
            raise NotImplementedError("Complement verified is not available at this time")
            rhs = funcs[root.children[0].label](x) - reduce(add, [funcs[child.label](x) for child in root.children[1:]], 0)
        elif root.strategy_verified:
            assert(len(root.children) == 0)
            rhs = root.eqv_path_objects[-1].get_genf(root.label, me, funcs[self.root.label](x), substitutions, fcache)
        elif root.recursion:
            assert(len(root.children) == 0)
            return []
        else:
            raise RuntimeError("WAT, this should not happen!")
        return reduce(add, [self._get_equations(child, me, funcs, substitutions, fcache) for child in root.children], [Eq(lhs, rhs)]) 


    def get_genf(self, verify=10, equations=False, expand=False, verbose=False):
        """Try to enumerate."""
        from sympy import solve
        from sympy.abc import x
        # TODO: interleaving decomposition
        funcs = self.get_funcs()
        f = funcs[self.root.label]
        me = self.root.eqv_path_objects[0]
        substitutions, fcache = {}, {}
        eqs = self.get_equations(me, funcs, substitutions, fcache)
        if verbose:
            print("The system of", len(eqs), "equations:")
            for eq in eqs:
                print(eq.lhs, "=", eq.rhs)
            print("\nThe", len(substitutions), "substitutions:")
            for k in sorted(substitutions.keys(), key=str):
                print(k, "=", substitutions[k])
            print()
            print("Solving...")
        solutions = solve(eqs, tuple([eq.lhs for eq in eqs]), dict=True, cubics=False, quartics=False, quintics=False)
        if verbose:
            print("Done!")
        # TODO: sanity check
        any_valid = False
        if solutions:
            permcounts = [len(list(me.gridded_perms_of_length(i))) for i in range(verify+1)]
            for solution in solutions:
                genf = solution[f(x)]
                genf = genf.subs(substitutions).doit().expand().simplify()
                try:
                    expansion = taylor_expand(genf, verify)
                except TypeError:
                    continue
                any_valid = True
                if permcounts == expansion:
                    sol = genf
                    if expand:
                        if equations:
                            return sol,[eq.subs(substitutions) for eq in eqs],expansion
                        return sol,expansion
                    if equations:
                        return sol,[eq.subs(substitutions) for eq in eqs]
                    return sol
            if any_valid:
                raise RuntimeError("Incorrect generating function\n" + str(solutions))
        raise RuntimeError("No solution was found for this tree")
        #return self.to_old_proof_tree().get_genf()

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
            eqv_objs = [css.objectdb.get_object(l) for l in eqv_path]
            eqv_explanations = [css.equivdb.get_explanation(x, y)
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
                #verified!
                eqv_path = css.equivdb.find_path(in_label, eqv_ver_label)
                eqv_objs = [css.objectdb.get_object(l) for l in eqv_path]
                eqv_explanations = [css.equivdb.get_explanation(x, y)
                                    for x, y in zip(eqv_path[:-1], eqv_path[1:])]

                formal_step = css.objectdb.verification_reason(eqv_ver_label)
                return ProofTreeNode(label, eqv_path, eqv_objs,
                                     eqv_explanations, strategy_verified=True,
                                     formal_step=formal_step)
            else:
                #recurse! we reparse these at the end, so recursed labels etc
                #are not interesting.
                return ProofTreeNode(label, [in_label],
                                    [css.objectdb.get_object(in_label)],
                                    formal_step="recurse",
                                    recursion=True)
        else:
            start, ends = css.rule_from_equivence_rule(root.label,
                                                       tuple(c.label
                                                             for c in root.children))
            formal_step = css.ruledb.explanation(start, ends)
            back_maps = css.ruledb.get_back_maps(start, ends)

            eqv_path = css.equivdb.find_path(in_label, start)
            eqv_objs = [css.objectdb.get_object(l) for l in eqv_path]
            eqv_explanations = [css.equivdb.get_explanation(x, y)
                                for x, y in zip(eqv_path[:-1], eqv_path[1:])]

            strat_children = []
            for next_label in ends:
                for child in root.children:
                    if css.equivdb.equivalent(next_label, child.label):
                        sub_tree = ProofTree.from_comb_spec_searcher_node(child,
                                                                          css,
                                                                          next_label)
                        strat_children.append(sub_tree)
                        break
            if back_maps is not None:
                #decomposition!
                return ProofTreeNode(label, eqv_path, eqv_objs,
                                     eqv_explanations, decomposition=True,
                                     back_maps=back_maps,
                                     formal_step=formal_step,
                                     children=strat_children)
            else:
                #batch!
                if "Complement" in formal_step:
                    return ProofTreeNode(label, eqv_path, eqv_objs,
                                         eqv_explanations,
                                         complement_verified=True,
                                         formal_step=formal_step)
                return ProofTreeNode(label, eqv_path, eqv_objs,
                                     eqv_explanations, disjoint_union=True,
                                     formal_step=formal_step,
                                     children=strat_children)

    def __eq__(self, other):
        return all(node1 == node2 for node1, node2 in zip(self.nodes(), other.nodes()))



def taylor_expand(genf, n=10):
    from sympy import Poly, O
    from sympy.abc import x
    num,den = genf.as_numer_denom()
    num = num.expand()
    den = den.expand()
    genf = num/den
    ser = Poly(genf.series(n=n+1).removeO(), x)
    res = ser.all_coeffs()
    res = res[::-1] + [0]*(n+1-len(res))
    return res
