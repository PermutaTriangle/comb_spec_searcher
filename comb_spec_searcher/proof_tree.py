"""
A proof tree class.

This can be used to get the generating function for the class.

The class is only used for reverse compatability with ComboPal. You should use
the Specification class.
"""
import json
import random
import warnings
from functools import reduce
from itertools import product
from operator import add, mul

import sympy
from logzero import logger

from .exception import InsaneTreeError, TaylorExpansionError
from .specification import CombinatorialSpecification
from .strategies.constructor import CartesianProduct, DisjointUnion
from .strategies.rule import EquivalencePathRule, Rule, VerificationRule
from .utils import (
    check_equation,
    check_poly,
    compositions,
    get_solution,
    maple_equations,
    taylor_expand,
)

__all__ = ("ProofTree",)


class ProofTreeNode:
    """Class is deprecated - use CombinatorialSpecification."""

    # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        label,
        eqv_path_labels,
        eqv_path_comb_classes,
        eqv_explanations=None,
        children=None,
        strategy_verified=False,
        decomposition=False,
        disjoint_union=False,
        recursion=False,
        formal_step="",
    ):
        self.label = label
        self.eqv_path_labels = eqv_path_labels
        self.eqv_path_comb_classes = eqv_path_comb_classes
        if eqv_explanations is not None:
            self.eqv_explanations = eqv_explanations
        else:
            self.eqv_explanations = []
        self.children = children if children is not None else []
        self.strategy_verified = strategy_verified
        self.decomposition = decomposition
        self.disjoint_union = disjoint_union
        self.recursion = recursion
        self.formal_step = formal_step
        self.terms = []
        self.recurse_node = None
        self.genf = None
        self.objects_of_length = dict()

    @property
    def logger_kwargs(self):
        """Class is deprecated - use CombinatorialSpecification."""
        return {"processname": "ProofTreeNode {}".format(self.label)}

    def to_jsonable(self):
        """Class is deprecated - use CombinatorialSpecification."""
        output = dict()
        output["label"] = self.label
        output["eqv_path_labels"] = list(self.eqv_path_labels)
        output["eqv_path_comb_classes"] = [
            x.to_jsonable() for x in self.eqv_path_comb_classes
        ]
        output["eqv_explanations"] = list(self.eqv_explanations)
        output["children"] = [child.to_jsonable() for child in self.children]
        output["strategy_verified"] = self.strategy_verified
        output["decomposition"] = self.decomposition
        output["disjoint_union"] = self.disjoint_union
        output["recursion"] = self.recursion
        output["formal_step"] = self.formal_step
        return output

    @classmethod
    def from_dict(cls, combclass, jsondict):
        """Class is deprecated - use CombinatorialSpecification."""
        if "eqv_path_objects" in jsondict:
            warnings.warn(
                (
                    "The 'eqv_path_objects' label is deprecated. You "
                    "should change this to 'eqv_path_comb_classes"
                    " in the future."
                ),
                DeprecationWarning,
                stacklevel=2,
            )
            jsondict["eqv_path_comb_classes"] = jsondict["eqv_path_objects"]
        return cls(
            label=jsondict["label"],
            eqv_path_labels=jsondict["eqv_path_labels"],
            eqv_path_comb_classes=[
                combclass.from_dict(x) for x in jsondict["eqv_path_comb_classes"]
            ],
            eqv_explanations=jsondict["eqv_explanations"],
            children=[
                ProofTreeNode.from_dict(combclass, child)
                for child in jsondict["children"]
            ],
            strategy_verified=jsondict["strategy_verified"],
            decomposition=jsondict["decomposition"],
            disjoint_union=jsondict["disjoint_union"],
            recursion=jsondict["recursion"],
            formal_step=jsondict["formal_step"],
        )

    @classmethod
    def from_json(cls, combclass, jsonstr):
        """Class is deprecated - use CombinatorialSpecification."""
        warnings.warn("ProofTreeNode is deprecated, use CombinatorialSpecification")
        jsondict = json.loads(jsonstr)
        return cls.from_dict(combclass, jsondict)

    @staticmethod
    def _error_string(
        parent, children, strat_type, formal_step, length, parent_total, children_total
    ):
        """Class is deprecated - use CombinatorialSpecification."""
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

    def random_sample(self, length):
        """Return a random object of the given length."""
        if self.disjoint_union:
            total = self.terms[length]
            if total == 0:
                raise ValueError(
                    (
                        "There is no object on node {} of length {}"
                        "".format(self.label, length)
                    )
                )
            children_totals = [(child, child.terms[length]) for child in self.children]
            choice = random.randint(1, total)
            # TODO: consider if there is an equivalent path to follow
            # TODO: Add functionality for bijection implied by rule
            sofar = 0
            for child, child_total in children_totals:
                sofar += child_total
                if choice <= sofar:
                    return child.random_sample(length)
            raise ValueError("You shouldn't be able to get here!")
        if self.decomposition:
            non_atom_children = [
                child for child in self.children if not child.is_atom()
            ]
            number_of_atoms = len(self.children) - len(non_atom_children)
            total = self.terms[length]
            choice = random.randint(1, total)
            sofar = 0
            for comp in compositions(length - number_of_atoms, len(non_atom_children)):
                subtotal = 1
                for i, child in zip(comp, non_atom_children):
                    subtotal *= child.terms[i]
                sofar += subtotal
                if choice <= sofar:
                    comp = list(reversed(comp))
                    sub_objs = [
                        (
                            child.random_sample((1 if child.is_atom() else comp.pop())),
                            child.eqv_path_comb_classes[0],
                        )
                        for child in self.children
                    ]
                    comb_class = self.eqv_path_comb_classes[-1]
                    return comb_class.from_parts(
                        *sub_objs, formal_step=self.formal_step
                    )
            raise ValueError("You shouldn't be able to get here.")
        if self.strategy_verified:
            return self.eqv_path_comb_classes[-1].random_sample(length)
        if self.recursion:
            return self.recurse_node.random_sample(length)
        raise NotImplementedError(
            (
                "Random sampler only implemented for "
                "disjoint union and cartesian "
                "product."
            )
        )

    def generate_objects_of_length(self, n):
        """Yield objects of given length."""
        if n in self.objects_of_length:
            yield from self.objects_of_length[n]
            return
        res = []
        # TODO: handle equivalence path nodes (somewhat assume length 1)
        if self.disjoint_union:
            for child in self.children:
                for path in child.generate_objects_of_length(n):
                    yield path
                    res.append(path)
        elif self.decomposition:
            comb_class = self.eqv_path_comb_classes[-1]
            child_comb_classes = [
                child.eqv_path_comb_classes[0] for child in self.children
            ]
            number_atoms = sum(1 for child in child_comb_classes if child.is_atom())
            for comp in compositions(
                n - number_atoms, len(self.children) - number_atoms
            ):
                i, actual_comp = 0, []
                for child in child_comb_classes:
                    if child.is_atom():
                        actual_comp.append(1)
                    else:
                        actual_comp.append(comp[i])
                        i += 1
                for child_objs in product(
                    *[
                        child.generate_objects_of_length(i)
                        for child, i in zip(self.children, actual_comp)
                    ]
                ):
                    parts = list(zip(child_objs, child_comb_classes))
                    path = comb_class.from_parts(*parts)
                    yield path
                    res.append(path)
        elif self.strategy_verified:
            for path in self.eqv_path_comb_classes[-1].objects_of_length(n):
                yield path
                res.append(path)
        else:
            if self.recursion:
                for path in self.recurse_node.generate_objects_of_length(n):
                    yield path
                    res.append(path)
            else:
                raise NotImplementedError(
                    (
                        "Object generator only implemented "
                        "for disjoint union and cartesian "
                        "product."
                    )
                )
        self.objects_of_length[n] = res

    def sanity_check(self, length, of_length=None):
        """Class is deprecated - use CombinatorialSpecification."""
        if of_length is None:
            raise ValueError("of_length is undefined.")

        number_objs = of_length(self.eqv_path_comb_classes[0], length)
        for i, comb_class in enumerate(self.eqv_path_comb_classes[1:]):
            eqv_number = of_length(comb_class, length)
            if number_objs != eqv_number:
                formal_step = ""
                for j in range(i + 1):
                    formal_step += self.eqv_explanations[j]
                return self._error_string(
                    self.eqv_path_comb_classes[0],
                    [comb_class],
                    "Equivalent",
                    formal_step,
                    length,
                    number_objs,
                    eqv_number,
                )
        if self.disjoint_union:
            child_comb_classes = [
                child.eqv_path_comb_classes[0] for child in self.children
            ]
            total = 0
            for comb_class in child_comb_classes:
                total += of_length(comb_class, length)
            if number_objs != total:
                return self._error_string(
                    self.eqv_path_comb_classes[0],
                    child_comb_classes,
                    "Batch",
                    self.formal_step,
                    length,
                    number_objs,
                    total,
                )
        if self.decomposition:
            child_comb_classes = [
                child.eqv_path_comb_classes[0] for child in self.children
            ]
            total = 0
            for part in compositions(length, len(child_comb_classes)):
                subtotal = 1
                for comb_class, partlen in zip(child_comb_classes, part):
                    if subtotal == 0:
                        break
                    subtotal *= of_length(comb_class, partlen)
                total += subtotal
            if number_objs != total:
                return self._error_string(
                    self.eqv_path_comb_classes[0],
                    child_comb_classes,
                    "Decomposition",
                    self.formal_step,
                    length,
                    number_objs,
                    total,
                )

    def __eq__(self, other):
        return all(
            [
                self.label == other.label,
                self.eqv_path_labels == other.eqv_path_labels,
                self.eqv_path_comb_classes == other.eqv_path_comb_classes,
                self.eqv_explanations == other.eqv_explanations,
                self.children == other.children,
                self.strategy_verified == other.strategy_verified,
                self.decomposition == other.decomposition,
                self.disjoint_union == other.disjoint_union,
                self.recursion == other.recursion,
                self.formal_step == other.formal_step,
            ]
        )

    def get_function(self, min_poly=False):
        """Class is deprecated - use CombinatorialSpecification."""
        if min_poly:
            return sympy.var("F_" + str(self.label))
        return sympy.Function("F_" + str(self.label))(sympy.abc.x)

    def get_equation(
        self, root_func=None, root_class=None, dummy_eq=False, min_poly=False, **kwargs
    ):
        """Class is deprecated - use CombinatorialSpecification."""
        lhs = self.get_function(min_poly)
        if self.disjoint_union:
            rhs = reduce(
                add, [child.get_function(min_poly) for child in self.children], 0
            )
        elif self.decomposition:
            rhs = reduce(
                mul, [child.get_function(min_poly) for child in self.children], 1
            )
        elif self.recursion:
            rhs = lhs
        elif self.strategy_verified:
            comb_class = self.eqv_path_comb_classes[-1]
            try:
                if min_poly:
                    lhs = comb_class.get_min_poly(
                        root_func=root_func, root_class=root_class
                    )
                    F = sympy.Symbol("F")
                    lhs = lhs.subs({F: self.get_function(min_poly)})
                    rhs = 0
                else:
                    rhs = comb_class.get_genf(
                        root_func=root_func, root_class=root_class
                    )
            except ValueError as e:
                if not dummy_eq:
                    raise ValueError(e)
                logger.info(
                    "Unable to find equation for %s, adding dummy"
                    "function. The comb class corresponding is\n%s",
                    lhs,
                    comb_class,
                    extra=self.logger_kwargs,
                )
                rhs = sympy.Function("DOITYOURSELF")(sympy.abc.x)
        else:
            if not dummy_eq:
                raise NotImplementedError("Using an unimplemented constructor")
            logger.info(
                "Unable to find equation for %s, adding dummy " "function.",
                lhs,
                extra=self.logger_kwargs,
            )
            rhs = sympy.Function("DOITYOURSELF")(sympy.abc.x)
        return sympy.Eq(lhs, rhs)

    def count_objects_of_length(self, n):
        """
            Calculates objects of length in each node according to the
            recurrence relation implied by the proof tree. Only works
            for disjoint union, decomposition, strategy verified and recursion.

            Verified nodes are expected to have a known generating function.
        """
        if n < 0:
            return 0
        if len(self.terms) > n and self.terms[n] is not None:
            return self.terms[n]

        ans = 0
        if self.disjoint_union:
            ans = sum(child.count_objects_of_length(n) for child in self.children)
        elif self.decomposition:
            # Number of children that are just the atom
            atoms = 0
            # Indices of children that are positive (do not contain epsilon)
            pos_children = set()
            children = []  # A list of children that are not atoms
            for child in self.children:
                if child.is_atom():
                    atoms += 1
                else:
                    if child.eqv_path_comb_classes[-1].is_positive():
                        pos_children.add(len(children))
                    children.append(child)

            for comp in compositions(n - atoms, len(children)):
                # A composition is only valid if all positive children
                # get more than 0 atoms.
                if any(c == 0 for i, c in enumerate(comp) if i in pos_children):
                    continue
                tmp = 1
                for i, child in enumerate(children):
                    tmp *= child.count_objects_of_length(comp[i])
                    if tmp == 0:
                        break
                ans += tmp
        elif self.strategy_verified:
            if self.is_epsilon():
                return 1 if n == 0 else 0
            if self.is_atom():
                return 1 if n == 1 else 0
            self._ensure_terms(n)
            return self.terms[n]
        elif self.recursion:
            if not self.recurse_node:
                raise ValueError(
                    (
                        "Recursing to a subtree that is not"
                        " contained in the subtree from the"
                        " root object that was called on."
                    )
                )
            return self.recurse_node.count_objects_of_length(n)
        else:
            raise NotImplementedError(
                (
                    "count_objects_of_length() is only "
                    "defined for disjoint union, "
                    "cartesian product, recursion "
                    "and strategy verified."
                )
            )
        if len(self.terms) <= n:
            self.terms.extend([None] * (n - len(self.terms) + 1))
        self.terms[n] = ans
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
        coeffs = taylor_expand(self.genf, n=n + expand_extra)
        self.terms.extend(coeffs[len(self.terms) :])

    def is_atom(self):
        """Class is deprecated - use CombinatorialSpecification."""
        return any(comb_class.is_atom() for comb_class in self.eqv_path_comb_classes)

    def is_epsilon(self):
        """Class is deprecated - use CombinatorialSpecification."""
        return any(comb_class.is_epsilon() for comb_class in self.eqv_path_comb_classes)

    @property
    def eqv_path_objects(self):
        """This is for reverse compatibility."""
        warnings.warn(
            (
                "The 'eqv_path_objects' label is deprecated. You "
                "should change this to 'eqv_path_comb_classes"
                " in the future."
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        return self.eqv_path_comb_classes


class ProofTree:
    """Class is deprecated - use CombinatorialSpecification."""

    def __init__(self, root):
        warnings.warn(
            (
                "The ProofTree class is deprecated."
                " Use CombinatorialSpecification instead."
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        if not isinstance(root, ProofTreeNode):
            raise TypeError("Root must be a ProofTreeNode.")
        self.root = root
        self._of_length_cache = {}
        self._fixed_recursion = False

    @property
    def logger_kwargs(self):
        """Class is deprecated - use CombinatorialSpecification."""
        return {"processname": "ProofTree"}

    def to_jsonable(self):
        """Class is deprecated - use CombinatorialSpecification."""
        return {"root": self.root.to_jsonable()}

    @classmethod
    def from_dict(cls, combclass, jsondict):
        """Class is deprecated - use CombinatorialSpecification."""
        root = ProofTreeNode.from_dict(combclass, jsondict["root"])
        return cls(root)

    @classmethod
    def from_json(cls, combclass, jsonstr):
        """Class is deprecated - use CombinatorialSpecification."""
        jsondict = json.loads(jsonstr)
        return cls.from_dict(combclass, jsondict)

    def _of_length(self, comb_class, length):
        """Class is deprecated - use CombinatorialSpecification."""
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
        root_class = kwargs.get("root_class")
        root_func = kwargs.get("root_func")
        if root_class is None:
            root_class = self.root.eqv_path_comb_classes[0]
            kwargs["root_class"] = root_class
        if root_func is None:
            first_call = True
            root_func = sympy.Symbol("F_root")
            kwargs["root_func"] = root_func
        else:
            first_call = False
        for node in self.nodes():
            if node.recursion:
                continue
            eqs.add(node.get_equation(dummy_eq=dummy_eqs, min_poly=min_poly, **kwargs))
        if first_call:
            eqs.add(sympy.Eq(self.root.get_function(min_poly=True), root_func))
        return eqs

    def get_genf(self, verify=8, only_root=True):
        """Find generating function for proof tree. Return None if no solution
        is found. If not verify will return list of possible solutions."""
        # TODO: add substitutions, so as to solve with symbols first.
        eqs = self.get_equations()
        root_class = self.root.eqv_path_comb_classes[0]
        root_func = self.root.get_function()
        eqs = self.get_equations(root_class=root_class, root_func=root_func)
        logger.info(
            maple_equations(
                root_func,
                [len(list(root_class.objects_of_length(i))) for i in range(6)],
                eqs,
            ),
            extra=self.logger_kwargs,
        )
        logger.info("Solving...", extra=self.logger_kwargs)

        solutions = sympy.solve(
            eqs,
            tuple([eq.lhs for eq in eqs]),
            dict=True,
            cubics=False,
            quartics=False,
            quintics=False,
        )

        if solutions:
            if not verify:
                return solutions
            logger.info("Solved, verifying solutions.", extra=self.logger_kwargs)
            if only_root:
                objcounts = [
                    len(list(root_class.objects_of_length(i)))
                    for i in range(verify + 1)
                ]
                for solution in solutions:
                    genf = solution[root_func]
                    try:
                        expansion = taylor_expand(genf, verify)
                    except TaylorExpansionError:
                        continue
                    if objcounts == expansion:
                        logger.info("The generating function is %s", genf)
                        return genf
            else:
                for solution in solutions:
                    final_answer = {}
                    for node in self.nodes():
                        if node.label in final_answer:
                            continue
                        comb_class = node.eqv_path_comb_classes[0]
                        func = node.get_function()
                        objcounts = [
                            len(list(comb_class.objects_of_length(i)))
                            for i in range(verify + 1)
                        ]
                        genf = solution[func]
                        try:
                            expansion = taylor_expand(genf, verify)
                        except TaylorExpansionError:
                            continue
                        if objcounts == expansion:
                            logger.info(
                                "The generating function for %s is %s", func, genf
                            )
                            final_answer[node.label] = genf
                        else:
                            break
                    else:
                        return final_answer
        if solutions:
            raise RuntimeError(("Incorrect generating function\n" + str(solutions)))

    def get_min_poly(self, **kwargs):
        """Return the minimum polynomial of the generating function F that is
        implied by the proof tree."""
        # pylint: disable=too-many-statements
        root_class = kwargs.get("root_class")
        root_func = kwargs.get("root_func")
        if root_class is None:
            root_class = self.root.eqv_path_comb_classes[0]
            kwargs["root_class"] = root_class
        if root_func is None:
            first_call = True
            root_func = sympy.Symbol("F_root")
            kwargs["root_func"] = root_func
        else:
            first_call = False
        solve = kwargs.get("solve", False)

        eqs = self.get_equations(min_poly=True, **kwargs)

        func = self.root.get_function(min_poly=True)
        comb_class = self.root.eqv_path_comb_classes[0]
        logger.info(
            maple_equations(
                func,
                [len(list(comb_class.objects_of_length(i))) for i in range(6)],
                eqs,
            ),
            extra=self.logger_kwargs,
        )
        logger.info(
            "Computing Groebner basis with 'elimination' order.",
            extra=self.logger_kwargs,
        )
        all_funcs = set(x for eq in eqs for x in eq.atoms(sympy.Symbol))
        all_funcs.remove(func)
        if sympy.abc.x in all_funcs:
            all_funcs.remove(sympy.abc.x)

        elimination = sympy.polys.orderings.ProductOrder(
            (sympy.polys.orderings.grevlex, lambda m: m[:-2]),
            (sympy.polys.orderings.grevlex, lambda m: m[-2:]),
        )

        basis = sympy.groebner(eqs, *all_funcs, sympy.abc.x, func, order=elimination)
        eqs = basis.polys

        verify = 5
        if basis.polys:
            comb_class = self.root.eqv_path_comb_classes[0]
            initial = [
                len(list(comb_class.objects_of_length(i))) for i in range(verify + 1)
            ]
            if not first_call:
                root_initial = [
                    len(list(root_class.objects_of_length(i)))
                    for i in range(verify + 1)
                ]
                root_kwargs = {"root_func": root_func, "root_initial": root_initial}

        F = sympy.Symbol("F")
        for poly in basis.polys:
            logger.debug(
                "Trying the minimum poly:\n%s\nwith the atoms\n%s\n",
                poly.as_expr(),
                poly.atoms(sympy.Symbol),
                extra=self.logger_kwargs,
            )
            if poly.atoms(sympy.Symbol) <= {func, sympy.abc.x}:
                logger.info(
                    "Trying the min poly:\n%s", poly.as_expr(), extra=self.logger_kwargs
                )
                eq = poly.as_expr()
                eq = eq.subs({func: F})
                if check_poly(eq, initial) or check_equation(eq, initial):
                    logger.info(
                        "The minimum polynomial is %s", eq, extra=self.logger_kwargs
                    )
                    if solve:
                        sol = get_solution(eq, initial)
                        logger.info(
                            "The generating function is %s",
                            sol,
                            extra=self.logger_kwargs,
                        )
                        return eq, sol
                    return eq
            elif poly.atoms(sympy.Symbol) <= {func, root_func, sympy.abc.x}:
                if first_call and sympy.abc.x not in poly.atoms(sympy.Symbol):
                    continue
                assert not solve
                eq = poly.as_expr()
                eq = eq.subs({func: F})
                if check_poly(eq, initial, **root_kwargs) or check_equation(
                    eq, initial, **root_kwargs
                ):
                    logger.info(
                        "The minimum polynomial is %s", eq, extra=self.logger_kwargs
                    )
                    return eq
        raise RuntimeError("Incorrect minimum polynomial\n{}".format(basis))

    def random_sample(self, length=100):
        """Class is deprecated - use CombinatorialSpecification."""
        if any(len(node.terms) < length + 1 for node in self.nodes()):
            logger.info(("Computing terms"))
            self._recursion_setup()
            for node in self.nodes():
                node.terms = [
                    node.count_objects_of_length(i) for i in range(length + 1)
                ]
        logger.info("Walking through tree")
        return self.root.random_sample(length)

    def nodes(self, root=None):
        """Class is deprecated - use CombinatorialSpecification."""
        if root is None:
            root = self.root
        yield root
        for child in root.children:
            for node in self.nodes(root=child):
                yield node

    def number_of_nodes(self):
        """Class is deprecated - use CombinatorialSpecification."""
        return len(list(self.nodes()))

    def number_of_comb_classes(self):
        """Class is deprecated - use CombinatorialSpecification."""
        count = 0
        for node in self.nodes():
            count += len(node.eqv_path_comb_classes)
        return count

    def comb_classes(self, root=None):
        """Class is deprecated - use CombinatorialSpecification."""
        for node in self.nodes():
            for comb_class in node.eqv_path_comb_classes:
                yield comb_class

    def sanity_check(self, length=8, raiseerror=True):
        """Class is deprecated - use CombinatorialSpecification."""
        overall_error = ""
        for comb_class in self.comb_classes():
            if comb_class.is_empty():
                error = "Combinatorial class is empty!\n{}\n" "".format(
                    repr(comb_class)
                )
                if raiseerror:
                    raise InsaneTreeError(error)
                overall_error += error
        for node in self.nodes():
            error = node.sanity_check(length, self._of_length)
            if error is not None:
                if raiseerror:
                    raise InsaneTreeError(error)
                overall_error += error
        if overall_error:
            return False, overall_error
        return True, "Sanity checked, all good at length {}".format(length)

    def expand_tree(self, pack, **kwargs):
        """
        Return a ProofTree that comes from expanding the strategy verified
        combinatorial classes using the StrategyPack 'pack'. If no tree is
        found return None.

        The function relies on CombinatorialSpecificationSearcher and its
        method 'auto_search'. It first created a universe with rules from
        'self', and then adds strategy_verified objects to the front of the
        queue. All classes are assumed to be expandable. The '**kwargs' are
        passed to the 'auto_search' method and the searcher init method.
        """
        # pylint: disable=import-outside-toplevel
        from .comb_spec_searcher import CombinatorialSpecificationSearcher

        Searcher = kwargs.get("css", CombinatorialSpecificationSearcher)
        root_class = self.root.eqv_path_comb_classes[0]
        css = Searcher(root_class, pack, **kwargs)
        # Remove the root class from the queue
        css.classqueue.next()

        def get_label(comb_class):
            css.classdb.add(comb_class, expandable=True)
            label = css.classdb.get_label(comb_class)
            css.try_verify(comb_class, label)
            return label

        for node in self.nodes():
            # pylint: disable=protected-access
            # Add the equivalence implied by the nodes equivalent classes.
            for (idx, c1), c2 in zip(
                enumerate(node.eqv_path_comb_classes[:-1]),
                node.eqv_path_comb_classes[1:],
            ):
                l1, l2 = get_label(c1), get_label(c2)
                explanation = node.eqv_explanations[idx]
                css._add_equivalent_rule(l1, l2, explanation, "equiv")
            if node.children:
                # Add the rule implied by the node to its children.
                constructor = (
                    "disjoint"
                    if node.disjoint_union
                    else "cartesian"
                    if node.decomposition
                    else "other"
                )
                explanation = node.formal_step
                parent = get_label(node.eqv_path_comb_classes[-1])
                children = [
                    get_label(child.eqv_path_comb_classes[0]) for child in node.children
                ]
                css._add_rule(parent, children, explanation, constructor)
            elif node.strategy_verified:
                ver_label = get_label(node.eqv_path_comb_classes[-1])
                css._add_to_queue(ver_label)
        return ProofTree.from_specification(css.auto_search(**kwargs))

    def _recursion_setup(self):
        """Class is deprecated - use CombinatorialSpecification."""
        label_to_node = dict()

        for node in self.nodes():
            if not node.recursion:
                label_to_node[node.label] = node

        for node in self.nodes():
            if node.recursion:
                node.recurse_node = label_to_node[node.label]

        self._fixed_recursion = True

    def count_objects_of_length(self, n):
        """Class is deprecated - use CombinatorialSpecification."""
        if not self._fixed_recursion:
            self._recursion_setup()
        return self.root.count_objects_of_length(n)

    def generate_objects_of_length(self, n):
        """Class is deprecated - use CombinatorialSpecification."""
        self._recursion_setup()
        yield from self.root.generate_objects_of_length(n)

    def __eq__(self, other):
        return all(node1 == node2 for node1, node2 in zip(self.nodes(), other.nodes()))

    @classmethod
    def from_specification(cls, spec: CombinatorialSpecification) -> "ProofTree":
        """Return a ProofTree from a CombinatorialSpecification."""
        nodes = dict()
        eqv_paths = dict()
        # find equivalence paths and setup nodes without equivalence and children
        for rule in spec.rules_dict.values():
            if isinstance(rule, EquivalencePathRule):
                eqv_path_labels = []
                eqv_path_comb_classes = []
                eqv_explanations = []
                for comb_class, eqv_rule in rule.eqv_path_rules():
                    eqv_path_labels.append(spec.get_label(comb_class))
                    eqv_path_comb_classes.append(comb_class)
                    eqv_explanations.append(eqv_rule.formal_step)
                eqv_path_comb_classes.append(rule.children[0])
                eqv_paths[rule.comb_class] = (
                    eqv_path_labels,
                    eqv_path_comb_classes,
                    eqv_explanations,
                )
            elif isinstance(rule, VerificationRule):
                nodes[rule.comb_class] = ProofTreeNode(
                    label=spec.get_label(rule.comb_class),
                    eqv_path_labels=[spec.get_label(rule.comb_class)],
                    eqv_path_comb_classes=[rule.comb_class],
                    eqv_explanations=[],
                    children=[],
                    strategy_verified=True,
                    formal_step=rule.formal_step,
                )
            elif isinstance(rule, Rule):
                nodes[rule.comb_class] = ProofTreeNode(
                    label=spec.get_label(rule.comb_class),
                    eqv_path_labels=[spec.get_label(rule.comb_class)],
                    eqv_path_comb_classes=[rule.comb_class],
                    eqv_explanations=[],
                    children=list(rule.children),
                    decomposition=isinstance(rule.constructor, CartesianProduct),
                    disjoint_union=isinstance(rule.constructor, DisjointUnion),
                    strategy_verified=False,
                    formal_step=rule.formal_step,
                )
            else:
                raise ValueError(f"Don't know what to do with the rule class of {rule}")

        # fix equiv paths and children
        for node in list(nodes.values()):
            if node.children:
                new_children = []
                for child in node.children:
                    if child in eqv_paths:
                        (
                            eqv_path_labels,
                            eqv_path_comb_classes,
                            eqv_explanations,
                        ) = eqv_paths[child]
                        eqv_node = nodes[eqv_path_comb_classes[-1]]
                        eqv_node.eqv_path_labels = eqv_path_labels
                        eqv_node.eqv_path_comb_classes = eqv_path_comb_classes
                        eqv_node.eqv_explanations = eqv_explanations
                        new_children.append(nodes[eqv_path_comb_classes[-1]])
                    else:
                        new_children.append(nodes[child])
                node.children = new_children
        # fix root in eqv paths
        if spec.root in eqv_paths:
            (eqv_path_labels, eqv_path_comb_classes, eqv_explanations) = eqv_paths[
                spec.root
            ]

            eqv_node = nodes.pop(eqv_path_comb_classes[-1])
            eqv_node.eqv_path_labels = eqv_path_labels
            eqv_node.eqv_path_comb_classes = eqv_path_comb_classes
            eqv_node.eqv_explanations = eqv_explanations
            nodes[spec.root] = eqv_node

        seen = set()
        queue = [spec.root]
        copy_nodes: dict = {**nodes}
        while copy_nodes and queue:
            curr = queue.pop()
            seen.add(curr)
            node = copy_nodes.pop(curr, None)
            if node is not None:
                node = nodes[curr]
                for i, child in enumerate(node.children):
                    if any(c in seen for c in child.eqv_path_comb_classes):
                        node.children[i] = ProofTreeNode(
                            label=child.label,
                            eqv_path_labels=child.eqv_path_labels,
                            eqv_path_comb_classes=child.eqv_path_comb_classes,
                            eqv_explanations=child.eqv_explanations,
                            children=[],
                            strategy_verified=False,
                            recursion=True,
                            formal_step="recurse",
                        )
                    else:
                        queue.append(child.eqv_path_comb_classes[-1])

        return ProofTree(nodes[spec.root])
