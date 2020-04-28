import logging
import os
import time
import warnings
from collections import defaultdict
from typing import Tuple, TYPE_CHECKING

import json
import logzero
import psutil
import sympy
from logzero import logger

from .class_db import ClassDB
from .class_queue import DefaultQueue
from .exception import InvalidOperationError, SpecificationNotFound
from .rule_db import RuleDB
from .specification import CombinatorialSpecification
from .strategies import Strategy, StrategyGenerator, StrategyPack
from .strategies.rule import Rule, VerificationRule
from .utils import (
    cssmethodtimer,
    cssiteratortimer,
)

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
        self.strategy_pack = strategy_pack
        self.debug = kwargs.get("debug", False)
        if not self.debug:
            logzero.loglevel(logging.INFO, True)
        else:
            logzero.loglevel(logging.DEBUG, True)
        self.kwargs = kwargs.get("function_kwargs", dict())
        self.logger_kwargs = kwargs.get("logger_kwargs", {"processname": "runner"})

        self.func_times = defaultdict(float)
        self.func_calls = defaultdict(int)

        self.kwargs["logger"] = self.logger_kwargs
        self.kwargs["symmetry"] = bool(strategy_pack.symmetries)

        self.classdb = ClassDB(type(start_class))
        self.classqueue = DefaultQueue(strategy_pack)
        self.ruledb = RuleDB()

        # initialise the run with start_class
        self.start_label = self.classdb.get_label(start_class)
        self.classqueue.add(self.start_label)
        self.tried_to_verify = set()
        self.symmetry_expanded = set()
        self.try_verify(start_class, self.start_label)
        if self.symmetries:
            self._symmetry_expand(start_class, self.start_label)

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

    def try_verify(self, comb_class, label):
        """
        Try to verify the combinatorial class.
        """
        if label not in self.tried_to_verify:
            for strategy in self.verification_strategies:
                if self.ruledb.is_verified(label):
                    break
                for start_label, end_labels, rule in self._expand_class_with_strategy(
                    comb_class, strategy, label
                ):
                    self._add_rule(start_label, end_labels, rule)
            self.tried_to_verify.add(label)

    @cssmethodtimer("is empty")
    def is_empty(self, comb_class, label):
        """Return True if a combinatorial class contains no objects, False
        otherwise."""
        empty = self.classdb.is_empty(comb_class, label)
        return empty

    def _expand(self, label, strategies, inferral: bool):
        """
        Will expand the combinatorial class with given label using the given
        strategies.
        """
        comb_class = self.classdb.get_class(label)
        if inferral:
            self._inferral_expand(comb_class, label, strategies)
        else:
            for strategy_generator in strategies:
                for start_label, end_labels, rule in self._expand_class_with_strategy(
                    comb_class, strategy_generator, label
                ):
                    self._add_rule(start_label, end_labels, rule)

    @cssiteratortimer("_expand_class_with_strategy")
    def _expand_class_with_strategy(
        self, comb_class, strategy_generator, label=None, initial=False
    ) -> Tuple[int, Tuple[int, ...], Rule]:
        """
        Will expand the class with given strategy. Return time taken.
        """
        if label is None:
            self.classdb.get_label(comb_class)
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
            if len(rule.children) == 1 and comb_class == rule.children[0]:
                logger.debug(
                    "The equivalence strategy %s returned the same "
                    "combinatorial class when applied to %r",
                    str(rule).split(" ")[1],
                    comb_class,
                    extra=self.logger_kwargs,
                )
                continue
            end_labels = [
                self.classdb.get_label(comb_class) for comb_class in rule.children
            ]
            logger.debug(
                "Adding combinatorial rule %s -> %s with constructor" " '%s'",
                label,
                tuple(end_labels),
                rule.constructor if end_labels else "verified",
                extra=self.logger_kwargs,
            )

            if any(self.ruledb.are_equivalent(label, l) for l in end_labels):
                # This says comb_class = comb_class, so we skip it, but mark
                # every other class as empty.
                for l in end_labels:
                    if not self.ruledb.are_equivalent(label, l):
                        self._add_empty_rule(l)
                if self.debug:
                    for l, c in zip(end_labels, rule.children):
                        if not self.ruledb.are_equivalent(label, l):
                            assert c.is_empty()

            yield label, end_labels, rule

    def _add_rule(self, start_label, end_labels, rule):
        """
        Add the cleaned rules labels.

        - try to verify children combinatorial classes
        - set workability of combinatorial classes
        - remove empty combinatorial classes
        - symmetry expand combinatorial classes
        - add class to classqueue
        """
        cleaned_end_labels = []
        for comb_class, child_label in zip(rule.children, end_labels):
            if self.symmetries and child_label not in self.symmetry_expanded:
                self._symmetry_expand(
                    comb_class, child_label
                )  # TODO: mark symmetries as empty where appropriate
            # Only applying is_empty check to comb classes that are
            # possibly empty.
            if rule.possibly_empty and self.is_empty(comb_class, child_label):
                logger.debug(
                    "Label %s is empty.", child_label, extra=self.logger_kwargs
                )
                continue
            if rule.workable:
                self.classqueue.add(child_label)
            if not rule.inferrable:
                self.classqueue.set_not_inferrable(child_label)
            if not rule.possibly_empty:
                self.classdb.set_empty(child_label, empty=False)

            self.try_verify(comb_class, child_label)

            cleaned_end_labels.append(child_label)

        if rule.ignore_parent:
            self.classqueue.set_stop_yielding(start_label)

        if not cleaned_end_labels:
            # this must be a verification strategy!
            assert isinstance(rule, VerificationRule), rule.formal_step
        self.ruledb.add(start_label, end_labels, rule)

    def _add_empty_rule(self, label):
        """Mark label as empty. Treated as verified as can count empty set."""
        self.classdb.set_empty(label, empty=True)

    def _symmetry_expand(self, comb_class, label):
        """Add symmetries of combinatorial class to the database."""
        sym_labels = set([label])
        for strategy_generator in self.symmetries:
            for start_label, end_labels, rule in self._expand_class_with_strategy(
                comb_class, strategy_generator, label=label
            ):
                sym_label = end_labels[0]
                self.ruledb.add(start_label, (sym_label,), rule)
                self.classqueue.set_stop_yielding(sym_label)
                sym_labels.add(sym_label)
        self.symmetry_expanded.update(sym_labels)

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
            for start_label, end_labels, rule in self._expand_class_with_strategy(
                comb_class, strategy_generator, label=label
            ):
                inf_class = rule.children[0]
                inf_label = end_labels[0]
                self._add_rule(start_label, end_labels, rule)
                self.classqueue.set_not_inferrable(start_label)
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
        """
        x = sympy.abc.x

        def get_function(comb_class):
            label = self.classdb.get_label(comb_class)
            eqv_label = self.ruledb.equivdb[label]
            return sympy.Function("F_{}".format(eqv_label))(x)

        eqs = set()
        for start, ends, strategy in self.ruledb.all_rules():
            parent = self.classdb.get_class(start)
            children = [self.classdb.get_class(l) for l in ends]
            rule = strategy(parent, children)
            try:
                eq = rule.get_equation(get_function)
            except NotImplementedError:
                logger.info(
                    "can't find generating function for {}."
                    " The comb class is:\n{}".format(
                        get_function(rule.comb_class), rule.comb_class
                    )
                )
                eq = sympy.Eq(
                    get_function(rule.comb_class),
                    sympy.Function("NOTIMPLEMENTED")(sympy.abc.x),
                )
            eqs.add(eq)
        return eqs

    def do_level(self):
        """Expand combinatorial classes in current queue. Combintorial classes
        found added to next."""
        for label, strategies, inferral in self.classqueue.do_level():
            self._expand(label, strategies, inferral)

    @cssiteratortimer("queue")
    def _labels_to_expand(self):
        yield from self.classqueue

    @cssmethodtimer("status")
    def status(self):
        """
        Return a string of the current status of the CombSpecSearcher.

        It includes:
        - number of combinatorial classes, and information about verification
        - the times spent in each of the main functions
        """
        status = "CSS status:\n"

        status += "\tMemory (alone and shared) currently in use: {}\n".format(
            self.get_mem()
        )

        total = sum(self.func_times.values())
        status += "\tTotal time accounted for is {} seconds.\n".format(round(total, 2))
        total_perc = 0
        for explanation in self.func_calls:
            count = self.func_calls[explanation]
            time_spent = self.func_times[explanation]
            percentage = int((time_spent * 100) / total)
            total_perc += total
            status += "\tApplied {} {} times. Time spent is {} seconds (~{}%).\n".format(
                explanation, count, round(time_spent, 2), percentage,
            )

        status += self.classdb.status() + "\n"
        status += self.classqueue.status() + "\n"
        status += self.ruledb.status()
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
            " class:\n{}\n".format(self.classdb.get_class(self.start_label))
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

        If 'smallest' is set to 'True' then the searcher will return a proof
        tree that is as small as possible.
        """
        auto_search_start = time.time()

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

        max_expansion_time = 0
        expanding = True
        while expanding:
            expansion_start = time.time()
            for label, strategies, inferral in self._labels_to_expand():
                if not self.ruledb.is_verified(label):
                    self._expand(label, strategies, inferral)
                if time.time() - expansion_start > max_expansion_time:
                    break
                if status_update is not None:
                    if time.time() - status_start > status_update:
                        status = "\nTime taken so far is {} seconds\n".format(
                            round(time.time() - auto_search_start, 2)
                        )
                        status += self.status()
                        logger.info(status, extra=self.logger_kwargs)
                        status_start = time.time()
            else:
                expanding = False
                logger.info("No more classes to expand.", extra=self.logger_kwargs)
            spec_search_start = time.time()
            specification = self.get_specification(smallest=smallest)

            if specification is not None:
                found_string = "Specification found {}\n".format(
                    time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
                )
                found_string += "Time taken was {} seconds\n".format(
                    round(time.time() - auto_search_start, 2)
                )
                found_string += self.status()
                found_string += json.dumps(specification.to_jsonable())
                logger.info(found_string, extra=self.logger_kwargs)
                return specification
            # worst case, search every hour
            multiplier = 100 // perc
            max_expansion_time = min(
                multiplier * (time.time() - spec_search_start), 3600
            )
            if max_time is not None:
                if time.time() - auto_search_start > max_time:
                    logger.info(self.status(), extra=self.logger_kwargs)
                    logger.warning(
                        "Exceeded maximum time. Aborting auto search.",
                        extra=self.logger_kwargs,
                    )
                    return

    @cssmethodtimer("get specification")
    def get_specification(self, smallest: bool = False):
        try:
            if smallest:
                if self.iterative:
                    raise InvalidOperationError("can't use iterative and smallest")
                rules, eqv_paths = self.ruledb.get_smallest_specification(
                    self.start_label
                )
            else:
                rules, eqv_paths = self.ruledb.get_specification_rules(
                    self.start_label, iterative=self.iterative
                )
        except SpecificationNotFound:
            return None
        start_class = self.classdb.get_class(self.start_label)
        eqv_paths = tuple(
            tuple(self.classdb.get_class(l) for l in path) for path in eqv_paths
        )
        return CombinatorialSpecification(
            start_class,
            [(self.classdb.get_class(label), rule) for label, rule in rules],
            eqv_paths,
        )
