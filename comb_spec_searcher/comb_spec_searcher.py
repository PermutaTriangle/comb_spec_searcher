# pylint: disable=too-many-lines
import json
import logging
import os
import time
import warnings
from base64 import b64decode, b64encode
from collections import defaultdict
from functools import reduce
from operator import add, mul
from typing import Any, Dict, Tuple, TYPE_CHECKING

import logzero
import psutil
import sympy
from logzero import logger

from comb_spec_searcher.utils import compositions

from .class_db import ClassDB
from .class_queue import DefaultQueue
from .rule_db import RuleDB
from .strategies import Strategy, StrategyGenerator, StrategyPack
from .strategies.rule import Rule, VerificationRule
from .tree_searcher import (
    iterative_proof_tree_finder,
    iterative_prune,
    proof_tree_generator_dfs,
    prune,
    random_proof_tree,
)
from .utils import get_func, get_func_name, get_module_and_func_names

if TYPE_CHECKING:
    from comb_spec_searcher import CombinatorialClass

warnings.simplefilter("once", Warning)


class CombinatorialSpecificationSearcher:
    """
    The CombinatorialSpecificationSearcher class.

    This is used to build up knowledge about a combinatorial_class with respect
    to the given strategies and search for a combinatorial specification.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(
        self, start_class: "CombinatorialClass", strategy_pack: StrategyPack, **kwargs
    ):
        """Initialise CombinatorialSpecificationSearcher."""
        self.start_class = start_class
        self.strategy_pack = strategy_pack
        self.debug = kwargs.get("debug", False)
        if not self.debug:
            logzero.loglevel(logging.INFO, True)
        else:
            logzero.loglevel(logging.DEBUG, True)
        self.kwargs = kwargs.get("function_kwargs", dict())
        self.logger_kwargs = kwargs.get("logger_kwargs", {"processname": "runner"})
        self.kwargs["logger"] = self.logger_kwargs
        self.kwargs["symmetry"] = bool(strategy_pack.symmetries)

        self.classdb = ClassDB(type(start_class))
        self.classqueue = DefaultQueue(strategy_pack)
        self.ruledb = RuleDB()

        self.classdb.add(start_class)
        self.start_label = self.classdb.get_label(start_class)
        self.classqueue.add(self.start_label)
        self.classqueue.set_workable(self.start_label)

        self._has_proof_tree = False

        self.strategy_times = defaultdict(float)  # type: Dict[str, float]
        self.strategy_expansions = defaultdict(int)  # type: Dict[str, int]
        self.symmetry_time = 0
        self.tree_search_time = 0
        self.prep_for_tree_search_time = 0
        self.queue_time = 0
        self._time_taken = 0
        self.class_genf = {}  # type: Dict[CombinatorialClass, Any]

    @property
    def verification_strategies(self):
        """The verification strategies from the strategy pack."""
        return self.strategy_pack.ver_strats

    @property
    def iterative(self):
        """The iterative parameter from the strategy pack."""
        return self.strategy_pack.iterative

    @property
    def symmetries(self):
        """The symmetries functions for the strategy pack."""
        return self.strategy_pack.symmetries

    def to_dict(self):
        return {
            "start_class": b64encode(self.start_class.compress()).decode(),
            "debug": self.debug,
            "kwargs": self.kwargs,
            "logger_kwargs": self.logger_kwargs,
            "initial_strategies": [
                get_module_and_func_names(
                    f, warn=True, logger_kwargs=self.logger_kwargs
                )
                for f in self.initial_strategies
            ],
            "strategy_generators": [
                [
                    get_module_and_func_names(
                        f, warn=True, logger_kwargs=self.logger_kwargs
                    )
                    for f in l
                ]
                for l in self.strategy_generators
            ],
            "inferral_strategies": [
                get_module_and_func_names(
                    f, warn=True, logger_kwargs=self.logger_kwargs
                )
                for f in self.inferral_strategies
            ],
            "verification_strategies": [
                get_module_and_func_names(
                    f, warn=True, logger_kwargs=self.logger_kwargs
                )
                for f in self.verification_strategies
            ],
            "iterative": self.iterative,
            "forward_equivalence": self.forward_equivalence,
            "symmetries": self.symmetries,
            "classdb": self.classdb.to_dict(),
            "classqueue": self.classqueue.to_dict(),
            "ruledb": self.ruledb.to_dict(),
            "start_label": self.start_label,
            "_has_proof_tree": self._has_proof_tree,
            "strategy_times": dict(self.strategy_times),
            "strategy_expansions": dict(self.strategy_expansions),
            "symmetry_time": self.symmetry_time,
            "tree_search_time": self.tree_search_time,
            "prep_for_tree_search_time": self.prep_for_tree_search_time,
            "queue_time": self.queue_time,
            "_time_taken": self._time_taken,
        }

    @classmethod
    def from_dict(cls, dict_, combinatorial_class):
        # pylint: disable=protected-access
        strategy_pack = StrategyPack(
            initial_strats=[
                get_func(*mod_func_name)
                for mod_func_name in dict_["initial_strategies"]
            ],
            ver_strats=[
                get_func(*mod_func_name)
                for mod_func_name in dict_["verification_strategies"]
            ],
            inferral_strats=[
                get_func(*mod_func_name)
                for mod_func_name in dict_["inferral_strategies"]
            ],
            expansion_strats=[
                [get_func(*mod_func_name) for mod_func_name in l]
                for l in dict_["strategy_generators"]
            ],
            name="recovered strategy pack",
        )

        kwargs = {
            "debug": dict_["debug"],
            "iterative": dict_["iterative"],
            "forward_equivalence": dict_["forward_equivalence"],
        }

        try:
            kwargs["logger_kwargs"] = dict_["logger_kwargs"]
        except KeyError:
            logger.warning("logger_kwargs could not be recovered")
        try:
            kwargs["function_kwargs"] = dict_["function_kwargs"]
        except KeyError:
            logger.warning("function_kwargs could not be recovered")
        b = b64decode(dict_["start_class"].encode())
        c = combinatorial_class.decompress(b)
        css = cls(c, strategy_pack, **kwargs)
        css.classdb = ClassDB.from_dict(dict_["classdb"], combinatorial_class)
        css.classqueue = DefaultQueue.from_dict(dict_["classqueue"])
        css.ruledb = RuleDB.from_dict(dict_["ruledb"])
        css.start_label = dict_["start_label"]
        css._has_proof_tree = dict_["_has_proof_tree"]
        css.strategy_times = defaultdict(int, dict_["strategy_times"])
        css.strategy_expansions = defaultdict(int, dict_["strategy_expansions"])
        css.symmetry_time = dict_["symmetry_time"]
        css.tree_search_time = dict_["tree_search_time"]
        css.prep_for_tree_search_time = dict_["prep_for_tree_search_time"]
        css.queue_time = dict_["queue_time"]
        css._time_taken = dict_["_time_taken"]
        return css

    def update_status(self, strategy, time_taken):
        """Update that it took 'time_taken' to expand a combinatorial class
        with strategy"""
        name = get_func_name(strategy)
        self.strategy_times[name] += time_taken
        self.strategy_expansions[name] += 1

    # this should be moved to the RuleDB

    def try_verify(self, comb_class, label, force=False):
        """
        Try to verify the combinatorial class.

        It will only try to verify combinatorial classes who have no equivalent
        combinatorial classes already verified. If force=True, it will try to
        verify combinatorial class if it is not already strategy verified.
        """
        if force:
            if self.classdb.is_strategy_verified(label):
                return
        elif self.ruledb.is_verified(label):
            return
        if self.classdb.is_strategy_verified(label) is None:
            for ver_strategy in self.verification_strategies:
                start = time.time()
                rule = ver_strategy(comb_class, **self.kwargs)
                self.update_status(ver_strategy, time.time() - start)
                if rule is not None and rule.children == tuple():
                    self.ruledb.add(label, tuple(), rule)
                    self.classdb.set_strategy_verified(label)
                    return
            self.classdb.set_strategy_verified(label, False)

    def is_empty(self, comb_class, label):
        """Return True if a combinatorial class contains no objects, False
        otherwise."""
        start = time.time()
        empty = self.classdb.is_empty(comb_class, label)
        self.update_status(self.is_empty, time.time() - start)
        return empty

    def _symmetric_classes(self, comb_class, explanation=False):
        """Return all symmetries of a combinatorial class.

        This function only works if symmetry strategies have been given to the
        CombinatorialSpecificationSearcher.
        """
        symmetric_classes = []
        for sym in self.symmetries:
            symmetric_class = sym(comb_class)
            if symmetric_class != comb_class:
                if explanation:
                    if all(x != symmetric_class for x, _ in symmetric_classes):
                        symmetric_classes.append(
                            (symmetric_class, str(sym).split(" ")[1])
                        )
                else:
                    if all(x != symmetric_class for x in symmetric_classes):
                        symmetric_class.append(symmetric_class)
        return symmetric_classes

    def _expand(self, label, strategies, inferral: bool):
        """
        Will expand the combinatorial class with given label using the given
        strategies.
        """
        start = time.time()
        comb_class = self.classdb.get_class(label)
        self.queue_time += time.time() - start
        if inferral:
            self._inferral_expand(comb_class, label, strategies)
        else:
            for strategy_generator in strategies:
                self._expand_class_with_strategy(comb_class, strategy_generator, label)

    def _expand_class_with_strategy(
        self, comb_class, strategy_generator, label=None, initial=False, inferral=False
    ):
        """
        Will expand the class with given strategy. Return time taken.

        If 'inferral' will return time also return inferred class and label.
        """
        if label is None:
            self.classdb.get_label(comb_class)
        print("=" * 20)
        print(comb_class)
        print(strategy_generator)
        print(label)
        print(initial)
        print(inferral)
        start = time.time()
        if isinstance(strategy_generator, Strategy):
            strategies = [strategy_generator(comb_class, **self.kwargs)]
        elif isinstance(strategy_generator, StrategyGenerator):
            strategies = strategy_generator(comb_class, **self.kwargs)
        else:
            raise TypeError(
                "The strategy is not a Strategy or StrategyGenerator:\n{}".format(
                    strategy_generator
                )
            )
        if inferral:
            inf_class = None
            inf_label = None
        print("RULES")
        for strategy in strategies:
            if isinstance(strategy, Strategy):
                rule = strategy(comb_class)
            elif isinstance(strategy, Rule):
                rule = strategy
            else:
                raise TypeError(
                    "Attempting to add non Rule type. A Strategy Generator's"
                    " __call__ method should yield Strategy or "
                    "Strategy(comb_class, children) object."
                )
            if rule.children is None:
                continue  # this means the strategy does not apply
            print(rule.formal_step)
            if inferral and len(rule.children) != 1:
                raise TypeError(("Attempting to infer with non " "inferral strategy."))
            if inferral and comb_class == rule.children[0]:
                logger.debug(
                    "The inferral strategy %s returned the same "
                    "combinatorial class when applied to %r",
                    str(rule).split(" ")[1],
                    comb_class,
                    extra=self.logger_kwargs,
                )
                continue
            labels = [
                self.classdb.get_label(comb_class) for comb_class in rule.children
            ]
            print(label, labels, [self.ruledb.are_equivalent(label, l) for l in labels])
            logger.debug(
                "Adding combinatorial rule %s -> %s with constructor" " '%s'",
                label,
                tuple(labels),
                rule.constructor,
                extra=self.logger_kwargs,
            )

            if any(self.ruledb.are_equivalent(label, l) for l in labels):
                # This says comb_class = comb_class, so we skip it, but mark
                # every other class as empty.
                for l in labels:
                    if not self.ruledb.are_equivalent(label, l):
                        self._add_empty_rule(l)
                # if self.debug:
                for l, c in zip(labels, rule.children):
                    if not self.ruledb.are_equivalent(label, l):
                        if not c.is_empty():
                            for ch in rule.children:
                                print(ch)
                        assert c.is_empty()

            start -= time.time()
            end_labels = self._rule_cleanup(rule, labels)
            start += time.time()

            if rule.ignore_parent:
                self.classqueue.set_stop_yielding(label)

            if not end_labels:
                # this must be a verification strategy!
                assert isinstance(rule, VerificationRule), rule.formal_step
            self.ruledb.add(label, end_labels, rule)

            for end_label in end_labels:
                self.classqueue.add(end_label)

        self.update_status(strategy_generator, time.time() - start)

        if inferral:
            return inf_class, inf_label

    def _add_empty_rule(self, label):
        """Mark label as empty. Treated as verified as can count empty set."""
        self.classdb.set_empty(label, empty=True)

    def _sanity_check_rule(self, start, ends, constructor, length=5):
        """
        Sanity check a rule that has been found up to the length given.
        (default: length=5)
        """
        start_class = self.classdb.get_class(start)
        end_classes = [self.classdb.get_class(e) for e in ends]
        start_count = [
            len(list(start_class.objects_of_length(i))) for i in range(length)
        ]
        end_counts = [
            [len(list(e.objects_of_length(i))) for i in range(length)]
            for e in end_classes
        ]

        if constructor == "equiv":
            assert len(end_classes) == 1
            assert start_count == end_counts[0]
        elif constructor == "disjoint":
            assert start_count == [sum(c[i] for c in end_counts) for i in range(length)]
        elif constructor == "cartesian":
            for i in range(length):
                total = 0
                for part in compositions(i, len(end_counts)):
                    subtotal = 1
                    for end_count, partlen in zip(end_counts, part):
                        if subtotal == 0:
                            break
                        subtotal *= end_count[partlen]
                    total += subtotal
                assert total == start_count[i]

    def _rule_cleanup(self, rule: Rule, labels: Tuple[int, ...]):
        """
        Return the cleaned rules labels.

        - try to verify combinatorial classes
        - set workability of combinatorial classes
        - remove empty combinatorial classes
        - symmetry expand combinatorial classes
        - add class to classqueue
        """
        end_labels = []
        for comb_class, label in zip(rule.children, labels):
            if self.symmetries:
                self._symmetry_expand(
                    comb_class
                )  # TODO: mark symmetries as empty where appropriate
            # Only applying is_empty check to comb classes that are
            # possibly empty.
            if rule.possibly_empty and self.is_empty(comb_class, label):
                logger.info("Label %s is empty.", label, extra=self.logger_kwargs)
                continue
            if rule.workable:
                self.classqueue.set_workable(label)
            if rule.inferrable or rule.workable:
                self.classqueue.add(label)
            elif not rule.possibly_empty:
                self.classdb.set_empty(label, empty=False)

            self.try_verify(comb_class, label)

            end_labels.append(label)

        return end_labels

    def _symmetry_expand(self, comb_class):
        """Add symmetries of combinatorial class to the database.
        # TODO: Move to the classdb"""
        start = time.time()
        if not self.classdb.is_symmetry_expanded(comb_class):
            for sym_comb_class, formal_step in self._symmetric_classes(
                comb_class, explanation=True
            ):
                self.classdb.add(
                    sym_comb_class, expanding_other_sym=True, symmetry_expanded=True
                )
                self.equivdb.union(
                    self.classdb.get_label(comb_class),
                    self.classdb.get_label(sym_comb_class),
                    formal_step,
                )
        self.symmetry_time += time.time() - start

    def _inferral_expand(self, comb_class, label, inferral_strategies, skip=None):
        """
        Inferral expand combinatorial class with given label and inferral
        strategies.

        It will apply all inferral strategies to an combinatorial class.
        Return True if combinatorial class is inferred.
        """
        if self.debug:
            assert comb_class == self.classdb.get_class(label)
        for i, strategy_generator in enumerate(inferral_strategies):
            if strategy_generator == skip:
                continue
            inf_class, inf_label = self._expand_class_with_strategy(
                comb_class, strategy_generator, label, inferral=True
            )
            if inf_class is not None:
                self.classqueue.set_not_inferrable(label)
                inferral_strategies = (
                    inferral_strategies[i + 1 :] + inferral_strategies[0 : i + 1]
                )
                self._inferral_expand(
                    inf_class, inf_label, inferral_strategies, skip=strategy_generator
                )
                break
        self.classqueue.set_not_inferrable(label)

    def get_equations(self, **kwargs):
        """
        Returns a set of equations for all rules currently found.

        If keyword substitutions=True is given, then will return the equations
        with complex functions replaced by symbols and a dictionary of
        substitutions.

        If keyword fake_verify=label it will verify label and return equations
        which are in a proof tree for the root assuming that label is verified.
        """
        raise NotImplementedError("not brought forward yet")
        if kwargs.get("substitutions"):
            # dictionary from comb_class to symbol, filled by the combinatorial
            # class' get_genf function.
            kwargs["symbols"] = {}
            # dictionary from symbol to genf, filled by the combinatorial
            # class' get_genf function.
            kwargs["subs"] = {}

        functions = {}

        def get_function(label):
            """Return sympy function with label."""
            label = self.equivdb[label]
            function = functions.get(label)
            if function is None:
                # pylint: disable=not-callable
                function = sympy.Function("F_" + str(label))(sympy.abc.x)
                functions[label] = function
            return function

        if kwargs.get("fake_verify"):
            rules_dict = self.tree_search_prep()
            if kwargs.get("fake_verify"):
                rules_dict[kwargs.get("fake_verify")].add(tuple())
            rules_dict = prune(rules_dict)
            verified_labels = set(rules_dict.keys())
            if kwargs.get("fake_verify"):
                if self.start_label not in verified_labels:
                    return set()
                strat_ver = set()

        equations = set()

        for start, ends in self.ruledb:
            if kwargs.get("fake_verify"):
                if self.equivdb[start] not in verified_labels or any(
                    self.equivdb[x] not in verified_labels for x in ends
                ):
                    continue
                strat_ver.add(start)
                strat_ver.update(ends)

            start_function = get_function(start)
            end_functions = (get_function(end) for end in ends)
            constructor = self.ruledb.constructor(start, ends)
            if constructor in ("disjoint", "equiv"):
                eq = sympy.Eq(start_function, reduce(add, end_functions, 0))
            elif constructor == "cartesian":
                eq = sympy.Eq(start_function, reduce(mul, end_functions, 1))
            else:
                raise NotImplementedError(
                    (
                        "Only handle cartesian and "
                        "disjoint. Don't understand"
                        " {}.".format(constructor)
                    )
                )
            equations.add(eq)

        kwargs["root_func"] = get_function(self.start_label)
        kwargs["root_class"] = self.start_class
        for label in self.classdb:
            if kwargs.get("fake_verify") and label not in strat_ver:
                continue
            if self.classdb.is_strategy_verified(label):
                try:
                    function = get_function(label)
                    comb_class = self.classdb.get_class(label)
                    gen_func = self.get_class_genf(comb_class, **kwargs)
                    eq = sympy.Eq(function, gen_func)
                    equations.add(eq)
                except Exception as e:  # pylint: disable=broad-except
                    logger.warning(
                        "Failed to find generating function for:\n%r\n"
                        "Verified as:\n%s\nThe error was:\n%s",
                        comb_class,
                        self.classdb.verification_reason(label),
                        e,
                        extra=self.logger_kwargs,
                    )

        if kwargs.get("substitutions"):
            return (
                equations,
                [sympy.Eq(lhs, rhs) for lhs, rhs in kwargs.get("subs").items()],
            )
        return equations

    def get_class_genf(self, comb_class, **kwargs):
        genf = self.class_genf.get(comb_class)
        if genf is None:

            def taylor_expand(genf, n=10):
                num, den = genf.as_numer_denom()
                num = num.expand()
                den = den.expand()
                genf = num / den
                ser = sympy.Poly(genf.series(n=n + 1).removeO(), sympy.abc.x)
                res = ser.all_coeffs()
                res = res[::-1] + [0] * (n + 1 - len(res))
                return res

            genf = sympy.sympify(comb_class.get_genf(**kwargs))
            if not kwargs["root_func"] in genf.atoms(sympy.Function):
                count = [len(list(comb_class.objects_of_length(i))) for i in range(9)]
                if taylor_expand(sympy.sympify(genf), 8) != count:
                    raise ValueError(
                        (
                            "Incorrect generating function "
                            "in database.\n" + repr(comb_class)
                        )
                    )
            self.class_genf[comb_class] = genf
        return genf

    def do_level(self):
        """Expand combinatorial classes in current queue. Combintorial classes
        found added to next."""
        start = time.time()
        queue_start = time.time()
        for label, strategies, inferral in self.classqueue.do_level():
            queue_start -= time.time()
            self._expand(label, strategies, inferral)
            queue_start += time.time()
        self.queue_time += time.time() - queue_start
        self._time_taken += time.time() - start

    def expand_classes(self, total):
        """Will send 'total' many classes to the expand function.
        Returns True if no more classes to expand. """
        start = time.time()
        count = 0
        while count < total:
            queue_start = time.time()
            try:
                label, strategies, inferral = next(self.classqueue)
            except StopIteration:
                return True
            self._expand(label, strategies, inferral)
            self.queue_time += time.time() - queue_start
            count += 1
        self._time_taken += time.time() - start

    def status(self):
        """
        Return a string of the current status of the CombSpecSearcher.

        It includes:
        - number of combinatorial classes, and information about verification
        - the times spent in each of the main functions
        """
        # pylint: disable=too-many-locals
        status = ""
        status += "Currently on 'level' {}\n".format(
            self.classqueue.levels_completed + 1
        )
        status += "Time spent searching so far: ~{} seconds\n".format(
            int(self._time_taken)
        )

        status += "Memory (alone and shared) currently in use: {}\n".format(
            self.get_mem()
        )
        all_labels = self.classdb.label_to_info.keys()
        status += "Total number of combinatorial classes found is {}\n".format(
            str(len(all_labels))
        )
        expandable = 0
        verified = 0
        strategy_verified = 0
        empty = 0
        equivalent_sets = set()
        verified_equiv_sets = set()
        for label in all_labels:
            if (
                not self.is_expanded(label)
                and not self.equivdb.is_verified(label)
                and not self.classdb.is_expanding_children_only(label)
                and self.classdb.is_expandable(label)
                and not self.classdb.is_expanding_other_sym(label)
            ):
                expandable += 1
            if self.equivdb.is_verified(label):
                verified += 1
                verified_equiv_sets.add(self.equivdb[label])
            if self.classdb.is_strategy_verified(label):
                strategy_verified += 1
            if self.classdb.is_empty(label):
                empty += 1
            equivalent_sets.add(self.equivdb[label])

        status += "Total number of expandable combinatorial classes is {}\n" "".format(
            expandable
        )
        status += "Total number of verified combinatorial classes is {}\n" "".format(
            verified
        )
        status += (
            "Total number of strategy verified combinatorial "
            "classes is {}\n".format(strategy_verified)
        )
        status += "Total number of empty combinatorial classes is {}\n" "".format(empty)

        status += "Total number of equivalent sets is {}\n" "".format(
            len(equivalent_sets)
        )
        status += "Total number of verified equivalent sets is {}\n" "".format(
            len(verified_equiv_sets)
        )

        status += "Total number of combinatorial rules is {}\n" "".format(
            len(list(self.ruledb))
        )

        status += "The size of the working queue is {}\n".format(
            len(self.classqueue.working)
        )
        status += "The size of the current queue is {}\n".format(
            len(self.classqueue.curr_level)
        )
        status += "The size of the next queue is {}\n".format(
            len(self.classqueue.next_level)
        )

        for strategy, number in self.strategy_expansions.items():
            status += "Applied {} to {} combinatorial classes\n".format(
                strategy, number
            )

        symme_perc = (
            0
            if self._time_taken == 0
            else int(self.symmetry_time / self._time_taken * 100)
        )
        strat_perc = 0

        for strategy, total_time in self.strategy_times.items():
            perc = 0 if self._time_taken == 0 else total_time / self._time_taken * 100
            strat_perc += perc
            status += "Time spent applying {}: {} seconds, ~{}%\n".format(
                strategy, int(total_time), int(perc)
            )

        if self.symmetries:
            status += ("Time spent symmetry applying:" "~{} seconds, ~{}%\n").format(
                int(self.symmetry_time), int(symme_perc)
            )

        queue_perc = (
            0 if self._time_taken == 0 else self.queue_time / self._time_taken * 100
        )

        prep_time = self.prep_for_tree_search_time

        prpts_perc = 0 if self._time_taken == 0 else prep_time / self._time_taken * 100

        tsrch_perc = (
            0
            if self._time_taken == 0
            else self.tree_search_time / self._time_taken * 100
        )

        status += "Time spent queueing: ~{} seconds, ~{}%\n".format(
            int(self.queue_time), int(queue_perc)
        )
        status += (
            "Time spent prepping for tree search: ~{} seconds, " "~{}%\n"
        ).format(int(prep_time), int(prpts_perc))
        status += "Time spent searching for tree: ~{} seconds, ~{}%\n".format(
            int(self.tree_search_time), int(tsrch_perc)
        )

        total_perc = strat_perc + symme_perc + queue_perc + prpts_perc + tsrch_perc
        status += "Total of ~{}% accounted for.\n".format(int(total_perc))
        return status

    @staticmethod
    def get_mem():
        """Return memory used by CombSpecSearcher - note this is actually the
        memory usage of the process that the instance of CombSpecSearcher was
        invoked."""
        mem = psutil.Process(os.getpid()).memory_info().rss
        if mem / 1024 ** 3 < 1:
            return str(round(mem / 1024 ** 2)) + " MiB"
        return str(round(mem / 1024 ** 3, 3)) + " GiB"

    def run_information(self):
        """Return string detailing what CombSpecSearcher is looking for."""
        start_string = (
            "Initialising CombSpecSearcher for the combinatorial"
            " class:\n{}\n".format(self.start_class)
        )
        start_string += str(self.strategy_pack)
        return start_string

    def auto_search(self, **kwargs):
        """
        An automatic search function.

        Classes will be expanded until a proof tree is found. A tree will be
        searched for approximately 1% of the search time. This can be set using
        the 'perc' keyword, as some percentage between 0 and 100.

        The search will continue, unless a proof tree is found. You can set the
        keyword 'max_time' to stop the search after 'max_time' many seconds.

        Information is logged to logger.info. It will also log the proof tree,
        in json format. For periodic status_updates, set the keyword flag
        'status_update', an update will be given every status_update seconds.

        If 'save' is set to 'True' as a keyword argument, a json string of
        CombSpecSearcher will be logged to logger.info if 'max_time' is passed.

        If a proof tree is found, and 'genf' is set to 'True' as a keyword
        argument, then if a proof tree is found, the searcher will call the
        'ProofTree.get_min_poly()' method, returning this output alongside the
        proof tree.

        If 'smallest' is set to 'True' then the searcher will return a proof
        tree that is as small as possible.
        """
        perc = kwargs.get("perc", 1)
        if not 0 < perc <= 100:
            logger.warning(
                (
                    "Percentage not between 0 and 100, so assuming 1%"
                    " search percentage."
                ),
                extra=self.logger_kwargs,
            )
            perc = 1
        status_update = kwargs.get("status_update", None)
        max_time = kwargs.get("max_time", None)
        smallest = kwargs.get("smallest", False)
        if status_update:
            status_start = time.time()
        start_string = "Auto search started {}\n".format(
            time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
        )
        start_string += self.run_information()
        logger.info(start_string, extra=self.logger_kwargs)

        max_search_time = 0
        expanding = True
        while expanding:
            start = time.time() + 0.00001
            while time.time() - start < max_search_time:
                if status_update is not None:
                    if time.time() - status_start > status_update:
                        status = self.status()
                        logger.info(status, extra=self.logger_kwargs)
                        status_start = time.time()
                if self.expand_classes(1):
                    # this function returns True if no more classes to expand
                    expanding = False
                    logger.info("No more classes to expand.", extra=self.logger_kwargs)
                    break
            start = time.time()
            if smallest:
                proof_tree = self.find_smallest_proof_tree()
            else:
                proof_tree = self.get_proof_tree()
            if proof_tree is not None:
                found_string = "Proof tree found {}\n".format(
                    time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
                )
                found_string += "Time taken was {} seconds\n\n".format(self._time_taken)
                found_string += self.status()
                found_string += json.dumps(proof_tree.to_jsonable())
                logger.info(found_string, extra=self.logger_kwargs)
                if kwargs.get("genf", False):
                    min_poly, func = proof_tree.get_min_poly(solve=True)
                    return proof_tree, min_poly, func
                return proof_tree
            # worst case, search every hour
            multiplier = 100 // perc
            max_search_time = min(multiplier * (time.time() - start), 3600)
            if max_time is not None:
                if self._time_taken > max_time:
                    logger.info(self.status(), extra=self.logger_kwargs)
                    if kwargs.get("save", False):
                        string = "The universe: \n"
                        string += json.dumps(self.to_dict())
                        logger.info(string, extra=self.logger_kwargs)
                    logger.warning(
                        "Exceeded maximum time. " "Aborting auto search.",
                        extra=self.logger_kwargs,
                    )
                    return

    # TODO: the functions below should be moved to the RuleDB

    def has_proof_tree(self):
        """Return True if a proof tree has been found, false otherwise."""
        return self._has_proof_tree

    def tree_search_prep(self):
        """
        Return rule dictionary ready for tree searcher.

        Converts all rules to be in terms of equivalence database.
        """
        start_time = time.time()
        rules_dict = self.ruledb.rules_up_to_equivalence()
        self.prep_for_tree_search_time += time.time() - start_time
        return rules_dict

    def _add_rule_to_rules_dict(self, rule, rules_dict):
        """Add a rule to given dictionary."""
        first, rest = rule
        eqv_first = self.equivdb[first]
        eqv_rest = tuple(sorted(self.equivdb[x] for x in rest))
        rules_dict[eqv_first] |= set((tuple(eqv_rest),))

    def equivalent_strategy_verified_label(self, label):
        """Return equivalent strategy verified label if one exists."""
        for eqv_label in self.equivdb.equivalent_set(label):
            if self.classdb.is_strategy_verified(eqv_label):
                return eqv_label

    def rule_from_equivence_rule(self, eqv_start, eqv_ends):
        """Return a rule that satisfies the equivalence rule."""
        for rule in self.ruledb:
            start, ends = rule
            if not self.equivdb.equivalent(start, eqv_start):
                continue
            if tuple(sorted(eqv_ends)) == tuple(sorted(self.equivdb[l] for l in ends)):
                return start, ends

    def find_tree(self):
        """Search for a random tree based on current data found."""
        start = time.time()

        rules_dict = self.tree_search_prep()

        # Prune all unverified labels (recursively)
        if self.iterative:
            rules_dict = iterative_prune(
                rules_dict, root=self.equivdb[self.start_label]
            )
        else:
            rules_dict = prune(rules_dict)

        # only verified labels in rules_dict, in particular, there is a proof
        # tree if the start label is in the rules_dict
        for label in rules_dict.keys():
            self.equivdb.update_verified(label)

        if self.ruledb.equivdb[self.start_label] in rules_dict:
            self._has_proof_tree = True
            if self.iterative:
                proof_tree = iterative_proof_tree_finder(
                    rules_dict, root=self.equivdb[self.start_label]
                )
            else:
                proof_tree = random_proof_tree(
                    rules_dict, root=self.equivdb[self.start_label]
                )
        else:
            proof_tree = None

        self.tree_search_time += time.time() - start
        self._time_taken += time.time() - start
        return proof_tree

    def get_proof_tree(self):
        """
        Return a random proof tree if one exists."""
        logger.debug("Searching for tree", extra=self.logger_kwargs)
        proof_tree_node = self.find_tree()
        if proof_tree_node is not None:
            proof_tree = ProofTree.from_comb_spec_searcher(proof_tree_node, self)
            assert proof_tree is not None
            return proof_tree

    def all_proof_trees(self):
        """A generator that yields all proof trees in the universe."""
        root_label = self.equivdb[self.start_label]

        rules_dict = self.tree_search_prep()
        # Prune all unverified labels (recursively)
        if self.iterative:
            rules_dict = iterative_prune(rules_dict, root=root_label)
        else:
            rules_dict = prune(rules_dict)

        if self.equivdb[self.start_label] in rules_dict:
            if self.iterative:
                raise NotImplementedError(
                    "There is no method for yielding all" " iterative proof trees."
                )
            proof_trees = proof_tree_generator_dfs(rules_dict, root=root_label)
        else:
            logger.info("There are no proof trees.")
            return
        for proof_tree_node in proof_trees:
            yield ProofTree.from_comb_spec_searcher(proof_tree_node, self)

    def find_smallest_proof_tree(self):
        """Return a smallest proof tree in the universe. It uses exponential
        search to find it."""
        if self.iterative:
            raise NotImplementedError(
                "There is no method for finding " " smallest iterative proof trees."
            )
        root_label = self.equivdb[self.start_label]
        logger.debug("Searching for tree", extra=self.logger_kwargs)
        rules_dict = self.tree_search_prep()
        rules_dict = prune(rules_dict)

        if not self.equivdb[self.start_label] in rules_dict:
            logger.debug("There are no proof trees.", extra=self.logger_kwargs)
            return
        bound = 1
        # Determine an upper bound on the size of a smallest proof tree.
        while True:
            logger.info(
                "Looking for tree with max size %s", bound, extra=self.logger_kwargs
            )
            try:
                tree = next(
                    proof_tree_generator_dfs(rules_dict, root=root_label, maximum=bound)
                )
                break
            except StopIteration:
                bound *= 2
        minimum = 1
        maximum = bound
        # Binary search to find a smallest proof tree.
        while minimum < maximum:
            middle = (minimum + maximum) // 2
            logger.info(
                "Looking for tree with max size %s", middle, extra=self.logger_kwargs
            )
            try:
                tree = next(
                    proof_tree_generator_dfs(
                        rules_dict, root=root_label, maximum=middle
                    )
                )
                maximum = middle
            except StopIteration:
                minimum = middle + 1
        return ProofTree.from_comb_spec_searcher(tree, self)
