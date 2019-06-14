"""
A proof tree class.

This can be used to get the generating function for the class.
"""
import json
import random
import sys
import warnings
from functools import reduce
from operator import add, mul

import sympy
from logzero import logger

from permuta.misc.ordered_set_partitions import partitions_of_n_of_size_k

from .tree_searcher import Node as tree_searcher_node
from .utils import (check_equation, check_poly, get_solution, maple_equations,
                    taylor_expand, compositions)


class ProofTreeNode(object):
    def __init__(self, label, eqv_path_labels, eqv_path_comb_classes,
                 eqv_explanations=[], children=[], strategy_verified=False,
                 decomposition=False, disjoint_union=False, recursion=False,
                 formal_step=""):
        self.label = label
        self.eqv_path_labels = eqv_path_labels
        self.eqv_path_comb_classes = eqv_path_comb_classes
        self.eqv_explanations = eqv_explanations
        self.children = children
        self.strategy_verified = strategy_verified
        self.decomposition = decomposition
        self.disjoint_union = disjoint_union
        self.recursion = recursion
        self.formal_step = formal_step
        self.sympy_function = None
        self.terms = []
        self.recurse_node = None
        self.genf = None

    @property
    def logger_kwargs(self):
        return {"processname": "ProofTreeNode {}".format(self.label)}

    def to_jsonable(self):
        output = dict()
        output['label'] = self.label
        output['eqv_path_labels'] = [x for x in self.eqv_path_labels]
        output['eqv_path_comb_classes'] = [x.to_jsonable()
                                           for x in self.eqv_path_comb_classes]
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
        if 'eqv_path_objects' in jsondict:
            warnings.warn(("The 'eqv_path_objects' label is deprecated. You "
                           "should change this to 'eqv_path_comb_classes"
                           " in the future."),
                          DeprecationWarning, stacklevel=2)
            jsondict['eqv_path_comb_classes'] = jsondict['eqv_path_objects']
        return cls(label=jsondict['label'],
                   eqv_path_labels=jsondict['eqv_path_labels'],
                   eqv_path_comb_classes=[
                                combclass.from_dict(x)
                                for x in jsondict['eqv_path_comb_classes']],
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
        error += "The parent comb class was:\n{}\n".format(parent.__repr__())
        error += "It produced {} many things\n".format(parent_total)
        error += "The children were:\n"
        for comb_class in children:
            error += comb_class.__repr__()
            error += "\n"
        error += "They produced {} many things\n\n".format(children_total)
        return error

    def random_sample(self, length, tree=None):
        """Return a random object of the given length."""
        def partitions(n, children_totals):
            if n == 0 and not children_totals:
                yield []
                return
            if len(children_totals) == 0 or n < 0:
                return
            start = children_totals[0]
            if len(children_totals) == 1:
                if start[n] != 0:
                    yield [n]
                return
            for i in range(n + 1):
                if start[i] == 0:
                    continue
                else:
                    for part in partitions(n - i, children_totals[1:]):
                        yield [i] + part

        if self.disjoint_union:
            total = self.terms[length]
            if total == 0:
                raise ValueError(("There is no object on node {} of length {}"
                                  "".format(self.label, length)))
            children_totals = [(child, child.terms[length])
                               for child in self.children]
            choice = random.randint(1, total)
            # TODO: consider if there is an equivalent path to follow
            # TODO: Add functionality for bijection implied by rule
            sofar = 0
            for child, child_total in children_totals:
                sofar += child_total
                if choice <= sofar:
                    return child.random_sample(length, tree)
            raise ValueError("You shouldn't be able to get here!")
        elif self.decomposition:
            total = self.terms[length]
            choice = random.randint(1, total)
            children_totals = [child.terms for child in self.children]
            sofar = 0
            for part in partitions(length, children_totals):
                subtotal = 1
                for i, terms in zip(part, children_totals):
                    subtotal *= terms[i]
                sofar += subtotal
                if choice <= sofar:
                    sub_objs = [(child.random_sample(i, tree),
                                 child.eqv_path_comb_classes[0])
                                for i, child in zip(part, self.children)]
                    comb_class = self.eqv_path_comb_classes[-1]
                    return comb_class.from_parts(*sub_objs,
                                                 formal_step=self.formal_step)
            raise ValueError("You shouldn't be able to get here.")
        elif self.strategy_verified:
            return self.eqv_path_comb_classes[-1].random_sample(length)
        else:
            if self.recursion:
                for node in tree.nodes():
                    if node.label == self.label and not node.recursion:
                        return node.random_sample(length, tree)
            raise NotImplementedError(("Random sampler only implemented for "
                                       "disjoint union and cartesian "
                                       "product."))

    def sanity_check(self, length, of_length=None):
        if of_length is None:
            raise ValueError("of_length is undefined.")

        number_objs = of_length(self.eqv_path_comb_classes[0], length)
        for i, comb_class in enumerate(self.eqv_path_comb_classes[1:]):
            eqv_number = of_length(comb_class, length)
            if number_objs != eqv_number:
                formal_step = ""
                for i in range(i+1):
                    formal_step += self.eqv_explanations[i]
                return self._error_string(self.eqv_path_comb_classes[0],
                                          [comb_class],
                                          "Equivalent",
                                          formal_step,
                                          length,
                                          number_objs,
                                          eqv_number)
        if self.disjoint_union:
            child_comb_classes = [child.eqv_path_comb_classes[0]
                                  for child in self.children]
            total = 0
            for comb_class in child_comb_classes:
                total += of_length(comb_class, length)
            if number_objs != total:
                return self._error_string(self.eqv_path_comb_classes[0],
                                          child_comb_classes,
                                          "Batch",
                                          self.formal_step,
                                          length,
                                          number_objs,
                                          total)
        if self.decomposition:
            child_comb_classes = [child.eqv_path_comb_classes[0]
                                  for child in self.children]
            total = 0
            for part in partitions_of_n_of_size_k(length,
                                                  len(child_comb_classes)):
                subtotal = 1
                for comb_class, partlen in zip(child_comb_classes, part):
                    if subtotal == 0:
                        break
                    subtotal *= of_length(comb_class, partlen)
                total += subtotal
            if number_objs != total:
                return self._error_string(self.eqv_path_comb_classes[0],
                                          child_comb_classes,
                                          "Decomposition",
                                          self.formal_step,
                                          length,
                                          number_objs,
                                          total)

    def __eq__(self, other):
        return all([self.label == other.label,
                    self.eqv_path_labels == other.eqv_path_labels,
                    self.eqv_path_comb_classes == other.eqv_path_comb_classes,
                    self.eqv_explanations == other.eqv_explanations,
                    self.children == other.children,
                    self.strategy_verified == other.strategy_verified,
                    self.decomposition == other.decomposition,
                    self.disjoint_union == other.disjoint_union,
                    self.recursion == other.recursion,
                    self.formal_step == other.formal_step])

    def get_function(self, min_poly=False):
        if min_poly:
            if (self.sympy_function is None or
                    isinstance(self.sympy_function, sympy.Function)):
                self.sympy_function = sympy.var("F_" + str(self.label))
        else:
            if (self.sympy_function is None or
                    isinstance(self.sympy_function, sympy.Symbol)):
                self.sympy_function = sympy.Function(
                                        "F_" + str(self.label))(sympy.abc.x)
        return self.sympy_function

    def get_equation(self, root_func=None, root_class=None,
                     dummy_eq=False, min_poly=False, **kwargs):
        lhs = self.get_function(min_poly)
        if self.disjoint_union:
            rhs = reduce(add,
                         [child.get_function(min_poly)
                          for child in self.children],
                         0)
        elif self.decomposition:
            rhs = reduce(mul,
                         [child.get_function(min_poly)
                          for child in self.children],
                         1)
        elif self.recursion:
            rhs = lhs
        elif self.strategy_verified:
            comb_class = self.eqv_path_comb_classes[-1]
            try:
                if min_poly:
                    lhs = comb_class.get_min_poly(root_func=root_func,
                                                  root_class=root_class)
                    F = sympy.Symbol("F")
                    lhs = lhs.subs({F: self.get_function(min_poly)})
                    rhs = 0
                else:
                    rhs = comb_class.get_genf(root_func=root_func,
                                              root_class=root_class)
            except ValueError as e:
                if not dummy_eq:
                    raise ValueError(e)
                logger.info(("Unable to find equation for {}, adding dummy"
                             "function. The comb class corresponding is\n{}"
                             "".format(lhs, comb_class)),
                            extra=self.logger_kwargs)
                rhs = sympy.Function("DOITYOURSELF")(sympy.abc.x)
        else:
            if not dummy_eq:
                raise NotImplementedError("Using an unimplemented constructor")
            logger.info(("Unable to find equation for {}, adding dummy "
                         "function.".format(lhs)),
                        extra=self.logger_kwargs)
            rhs = sympy.Function("DOITYOURSELF")(sympy.abc.x)
        return sympy.Eq(lhs, rhs)

    def count_objects_of_length(self, n):
        '''
            Calculates objects of lenght in each node according to the recurrence relation
            implied by the proof tree. Only works for disjoint union, decomposition,
            strategy verified and recursion.

            Verified nodes are expected to have a known generating function.
        '''
        if n < 0:
            return 0
        if len(self.terms) > n:
            return self.terms[n]

        ans = 0
        if self.disjoint_union:
            ans = sum(child.count_objects_of_length(n) for child in self.children)
        elif self.decomposition:
            atoms = 0 # Number of children that are just the atom
            pos_children = set() # Indices of children that are positive (do not contain epsilon)
            children = [] # A list of children that are not atoms
            for child in self.children:
                if child.eqv_path_comb_classes[-1].is_atom():
                    atoms += 1
                else:
                    if child.eqv_path_comb_classes[-1].is_positive():
                        pos_children.add(len(children))
                    children.append(child)

            for comp in compositions(n-atoms, len(children)):
                # A composition is only valid if all positive children get more than 0 atoms.
                if any(c == 0 for i,c in enumerate(comp) if i in pos_children):
                    continue
                tmp = 1
                for i, child in enumerate(children):
                    tmp *= child.count_objects_of_length(comp[i])
                    if tmp == 0:
                        break
                ans += tmp
        elif self.strategy_verified:
            if self.eqv_path_comb_classes[-1].is_epsilon():
                return 1 if n == 0 else 0
            elif self.eqv_path_comb_classes[-1].is_atom():
                return 1 if n == 1 else 0
            else:
                self._ensure_terms(n)
                return self.terms[n]
        elif self.recursion:
            if self.recurse_node:
                return self.recurse_node.count_objects_of_length(n)
            else:
                raise ValueError(("Recursing to a subtree that is not contained "
                                  "in the subtree from the root object that "
                                  "was called on."))
        else:
            raise NotImplementedError(("count_objects_of_length() is only "
                                       "defined for disjoint union, "
                                       "cartesian product, recursion "
                                       "and strategy verified."))
        if len(self.terms) != n:
            self.terms.extend([0]*(n-len(self.terms)))
        self.terms.append(ans)
        return ans

    def _ensure_terms(self, n, expand_extra=50):
        """
            Ensures that self.terms contains the n-th term. If not it will
            use the generating function to compute terms up to n+expand_extra.
        """
        if len(self.terms) > n:
            return
        if self.genf is None:
            self.genf = self.eqv_path_comb_classes[-1].get_genf()
        coeffs = taylor_expand(self.genf, n=n+expand_extra)
        self.terms.extend(coeffs[len(self.terms):])

    @property
    def eqv_path_objects(self):
        """This is for reverse compatability."""
        warnings.warn(("The 'eqv_path_objects' label is deprecated. You "
                       "should change this to 'eqv_path_comb_classes"
                       " in the future."),
                      DeprecationWarning, stacklevel=2)
        return self.eqv_path_comb_classes


class InsaneTreeError(Exception):
    pass


class ProofTree(object):
    def __init__(self, root):
        if not isinstance(root, ProofTreeNode):
            raise TypeError("Root must be a ProofTreeNode.")
        self.root = root
        self._of_length_cache = {}
        self._fixed_recursion = False

    @property
    def logger_kwargs(self):
        return {'processname': 'ProofTree'}

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

    def _of_length(self, comb_class, length):
        if comb_class not in self._of_length_cache:
            self._of_length_cache[comb_class] = {}

        number = self._of_length_cache[comb_class].get(length)

        if number is None:
            number = len(list(comb_class.objects_of_length(length)))
            self._of_length_cache[comb_class][length] = number

        return number

    def print_equivalences(self):
        """Return a string showing the equivalences."""
        s = ""
        for node in self.nodes():
            s += "===============\n"
            s += str(node.label) + "\n"
            for comb_class in node.eqv_path_comb_classes:
                s += str(comb_class) + "\n"

    def get_equations(self, dummy_eqs=False, min_poly=False, **kwargs):
        """Return the set of equations implied by the proof tree. If
        dummy_eqs=True then it will give a 'F_DOITYOURSELF' variable for
        equations that fail."""
        eqs = set()
        root_class = kwargs.get('root_class')
        root_func = kwargs.get('root_func')
        if root_class is None:
            root_class = self.root.eqv_path_comb_classes[0]
            kwargs['root_class'] = root_class
        if root_func is None:
            first_call = True
            root_func = sympy.Symbol("F_root")
            kwargs['root_func'] = root_func
        else:
            first_call = False
        for node in self.nodes():
            if node.recursion:
                continue
            eqs.add(node.get_equation(dummy_eq=dummy_eqs,
                                      min_poly=min_poly,
                                      **kwargs))
        if first_call:
            eqs.add(sympy.Eq(self.root.get_function(min_poly=True),
                             root_func))
        return eqs

    def get_genf(self, verify=8, only_root=True):
        """Find generating function for proof tree. Return None if no solution
        is found. If not verify will return list of possible solutions."""
        # TODO: add substitutions, so as to solve with symbols first.
        eqs = self.get_equations()
        root_class = self.root.eqv_path_comb_classes[0]
        root_func = self.root.get_function()
        eqs = self.get_equations(root_class=root_class, root_func=root_func)
        logger.info(maple_equations(root_func, root_class, eqs),
                    extra=self.logger_kwargs)
        logger.info("Solving...", extra=self.logger_kwargs)

        solutions = sympy.solve(eqs, tuple([eq.lhs for eq in eqs]),
                                dict=True, cubics=False, quartics=False,
                                quintics=False)

        if solutions:
            if not verify:
                return solutions
            logger.info("Solved, verifying solutions.",
                        extra=self.logger_kwargs)
            if only_root:
                objcounts = [len(list(root_class.objects_of_length(i)))
                             for i in range(verify + 1)]
                for solution in solutions:
                    genf = solution[root_func]
                    try:
                        expansion = taylor_expand(genf, verify)
                    except Exception as e:
                        continue
                    if objcounts == expansion:
                        logger.info(("The generating function is {}"
                                     "".format(genf)))
                        return genf
            else:
                for solution in solutions:
                    final_answer = {}
                    for node in self.nodes():
                        if node.label in final_answer:
                            continue
                        comb_class = node.eqv_path_comb_classes[0]
                        func = node.get_function()
                        objcounts = [len(list(comb_class.objects_of_length(i)))
                                     for i in range(verify + 1)]
                        genf = solution[func]
                        try:
                            expansion = taylor_expand(genf, verify)
                        except Exception as e:
                            continue
                        if objcounts == expansion:
                            logger.info(("The generating function for {} is {}"
                                         "".format(func, genf)))
                            final_answer[node.label] = genf
                        else:
                            break
                    else:
                        return final_answer
        if solutions:
            raise RuntimeError(("Incorrect generating function\n" +
                                str(solutions)))

    def get_min_poly(self, **kwargs):
        """Return the minimum polynomial of the generating function F that is
        implied by the proof tree."""
        root_class = kwargs.get('root_class')
        root_func = kwargs.get('root_func')
        if root_class is None:
            root_class = self.root.eqv_path_comb_classes[0]
            kwargs['root_class'] = root_class
        if root_func is None:
            first_call = True
            root_func = sympy.Symbol("F_root")
            kwargs['root_func'] = root_func
        else:
            first_call = False
        solve = kwargs.get('solve', False)

        eqs = self.get_equations(min_poly=True, **kwargs)

        func = self.root.get_function(min_poly=True)
        comb_class = self.root.eqv_path_comb_classes[0]
        logger.info(maple_equations(func, comb_class, eqs),
                    extra=self.logger_kwargs)
        logger.info("Computing Groebner basis with 'elimination' order.",
                    extra=self.logger_kwargs)
        all_funcs = set(x for eq in eqs for x in eq.atoms(sympy.Symbol))
        all_funcs.remove(func)
        if sympy.abc.x in all_funcs:
            all_funcs.remove(sympy.abc.x)

        elimination = sympy.polys.orderings.ProductOrder(
                (sympy.polys.orderings.grevlex, lambda m: m[:-2]),
                (sympy.polys.orderings.grevlex, lambda m: m[-2:])
        )

        basis = sympy.groebner(eqs, *all_funcs, sympy.abc.x, func,
                               order=elimination)
        eqs = basis.polys

        verify = 5
        if basis.polys:
            comb_class = self.root.eqv_path_comb_classes[0]
            initial = [len(list(comb_class.objects_of_length(i)))
                       for i in range(verify + 1)]
            if not first_call:
                root_initial = [len(list(root_class.objects_of_length(i)))
                                for i in range(verify + 1)]
                root_kwargs = {"root_func": root_func,
                               "root_initial": root_initial}

        F = sympy.Symbol("F")
        for poly in basis.polys:
            logger.debug(("Trying the minimum poly:\n{}\nwith the atoms\n{}\n"
                          "".format(poly.as_expr(), poly.atoms(sympy.Symbol))),
                         extra=self.logger_kwargs)
            if poly.atoms(sympy.Symbol) <= {func, sympy.abc.x}:
                logger.info("Trying the min poly:\n{}".format(poly.as_expr()),
                            extra=self.logger_kwargs)
                eq = poly.as_expr()
                eq = eq.subs({func: F})
                if check_poly(eq, initial) or check_equation(eq, initial):
                    logger.info(("The minimum polynomial is {}".format(eq)),
                                extra=self.logger_kwargs)
                    if solve:
                        sol = get_solution(eq, initial)
                        logger.info(("The generating function is {}"
                                     "".format(sol)), extra=self.logger_kwargs)
                        return eq, sol
                    else:
                        return eq
            elif poly.atoms(sympy.Symbol) <= {func, root_func, sympy.abc.x}:
                if first_call and sympy.abc.x not in poly.atoms(sympy.Symbol):
                    continue
                assert not solve
                eq = poly.as_expr()
                eq = eq.subs({func: F})
                if (check_poly(eq, initial, **root_kwargs) or
                        check_equation(eq, initial, **root_kwargs)):
                    logger.info(("The minimum polynomial is {}".format(eq)),
                                extra=self.logger_kwargs)
                    return eq
        raise RuntimeError(("Incorrect minimum polynomial\n" +
                            str(basis)))

    def random_sample(self, length=100, solved=False):
        if any(len(node.terms) < length + 1 for node in self.nodes()):
            logger.info(("Computing terms"))
            funcs = self.get_genf(only_root=False)
            for node in self.nodes():
                if len(node.terms) < length + 1:
                    logger.info(("Taylor expanding function {} to length {}."
                                 "".format(node.get_function(), length)))
                    node.terms = taylor_expand(funcs[node.label], length)
        logger.info("Walking through tree")
        return self.root.random_sample(length, self)

    def nodes(self, root=None):
        if root is None:
            root = self.root
        yield root
        for child in root.children:
            for node in self.nodes(root=child):
                yield node

    def number_of_nodes(self):
        return len(list(self.nodes()))

    def number_of_comb_classes(self):
        count = 0
        for node in self.nodes():
            count += len(node.eqv_path_comb_classes)
        return count

    def comb_classes(self, root=None):
        for node in self.nodes():
            for comb_class in node.eqv_path_comb_classes:
                yield comb_class

    def sanity_check(self, length=8, raiseerror=True):
        overall_error = ""
        for comb_class in self.comb_classes():
            if comb_class.is_empty():
                error = ("Combinatorial class is empty!\n{}\n"
                         "".format(repr(comb_class)))
                if raiseerror:
                    raise InsaneTreeError(error)
                else:
                    overall_error += error
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
            eqv_comb_classes = [css.classdb.get_class(l) for l in eqv_path]
            eqv_explanations = [css.equivdb.get_explanation(x, y,
                                                            one_step=True)
                                for x, y in zip(eqv_path[:-1], eqv_path[1:])]

            root.eqv_path_labels = eqv_path
            root.eqv_path_comb_classes = eqv_comb_classes
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
                eqv_comb_classes = [css.classdb.get_class(l) for l in eqv_path]
                eqv_explanations = [css.equivdb.get_explanation(x, y,
                                                                one_step=True)
                                    for x, y in zip(eqv_path[:-1],
                                                    eqv_path[1:])]

                formal_step = css.classdb.verification_reason(eqv_ver_label)
                return ProofTreeNode(label, eqv_path, eqv_comb_classes,
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
            eqv_comb_classes = [css.classdb.get_class(l) for l in eqv_path]
            eqv_explanations = [css.equivdb.get_explanation(x, y,
                                                            one_step=True)
                                for x, y in zip(eqv_path[:-1], eqv_path[1:])]

            strat_children = []
            ends = list(ends)
            for child in root.children:
                for next_label in ends:
                    if css.equivdb.equivalent(next_label, child.label):
                        ends.remove(next_label)
                        sub_tree = ProofTree.from_comb_spec_searcher_node(
                                                        child, css, next_label)
                        strat_children.append(sub_tree)
                        break

            if constructor == 'cartesian':
                # decomposition!
                return ProofTreeNode(label, eqv_path, eqv_comb_classes,
                                     eqv_explanations, decomposition=True,
                                     formal_step=formal_step,
                                     children=strat_children)
            elif constructor == 'disjoint' or constructor == 'equiv':
                # batch!
                return ProofTreeNode(label, eqv_path, eqv_comb_classes,
                                     eqv_explanations, disjoint_union=True,
                                     formal_step=formal_step,
                                     children=strat_children)
            elif constructor == 'other':
                return ProofTreeNode(label, eqv_path, eqv_comb_classes,
                                     eqv_explanations,
                                     formal_step=formal_step,
                                     children=strat_children)
            else:
                logger.debug(("Unknown constructor '{}' of type '{}'. "
                              "Use 'other' instead."
                              "".format(constructor, type(constructor))),
                             extra={"processname": "css_to_proof_tree"})
                raise NotImplementedError("Only handle cartesian and disjoint")

    def _recursion_setup(self):
        label_to_node = dict()

        for node in self.nodes():
            if not node.recursion:
                label_to_node[node.label] = node

        for node in self.nodes():
            if node.recursion:
                node.recurse_node = label_to_node[node.label]

        self._fixed_recursion = True

    def count_objects_of_length(self, n):
        if not self._fixed_recursion:
            self._recursion_setup()
        return self.root.count_objects_of_length(n)

    def __eq__(self, other):
        return all(node1 == node2
                   for node1, node2 in zip(self.nodes(), other.nodes()))
