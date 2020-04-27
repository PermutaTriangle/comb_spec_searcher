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
from .exception import SpecificationNotFound
from .rule_db import RuleDB
from .specification import CombinatorialSpecification
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

        self._has_proof_tree = False

        self.strategy_times = defaultdict(float)  # type: Dict[str, float]
        self.strategy_expansions = defaultdict(int)  # type: Dict[str, int]
        self.symmetry_time = 0
        self.tree_search_time = 0
        self.prep_for_tree_search_time = 0
        self.queue_time = 0
        self._time_taken = 0
        self.class_genf = {}  # type: Dict[CombinatorialClass, Any]

        # initialise the run with start_class
        self.start_label = self.classdb.get_label(start_class)
        self.classqueue.add(self.start_label)
        self.tried_to_verify = set()
        self.symmetry_expanded = set()
        self.try_verify(self.start_class, start_class)

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

    def update_status(self, strategy, time_taken):
        """Update that it took 'time_taken' to expand a combinatorial class
        with strategy"""
        name = get_func_name(strategy)
        self.strategy_times[name] += time_taken
        self.strategy_expansions[name] += 1

    # this should be moved to the RuleDB

    def try_verify(self, comb_class, label):
        """
        Try to verify the combinatorial class.
        """
        if label not in self.tried_to_verify:
            for strategy in self.verification_strategies:
                if self.ruledb.is_verified(label):
                    break
                self._expand_class_with_strategy(comb_class, strategy, label)
            self.tried_to_verify.add(label)

    def is_empty(self, comb_class, label):
        """Return True if a combinatorial class contains no objects, False
        otherwise."""
        start = time.time()
        empty = self.classdb.is_empty(comb_class, label)
        self.update_status(self.is_empty, time.time() - start)
        return empty

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
        # print("=" * 20)
        # print(comb_class)
        # print(label, strategy_generator)
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
        # print("RULES")
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
            # print(rule)
            if rule.children is None:
                continue  # this means the strategy does not apply
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
            # print(rule.formal_step, label, labels)
            logger.debug(
                "Adding combinatorial rule %s -> %s with constructor" " '%s'",
                label,
                tuple(labels),
                rule.constructor if labels else "verified",
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
                        # print(
                        #     [
                        #         len(list(comb_class.objects_of_length(i)))
                        #         for i in range(6)
                        #     ]
                        # )
                        # if not c.is_empty():
                        # print(l)
                        # for ch in rule.children:
                        #     print(ch)
                        #     print(
                        #         [
                        #             len(list(ch.objects_of_length(i)))
                        #             for i in range(6)
                        #         ]
                        #     )
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
                    comb_class, label
                )  # TODO: mark symmetries as empty where appropriate
            # Only applying is_empty check to comb classes that are
            # possibly empty.
            if rule.possibly_empty and self.is_empty(comb_class, label):
                logger.debug("Label %s is empty.", label, extra=self.logger_kwargs)
                continue
            if rule.workable:
                self.classqueue.add(label)
            if not rule.inferrable:
                self.classqueue.set_not_inferrable(label)
            if not rule.possibly_empty:
                self.classdb.set_empty(label, empty=False)

            self.try_verify(comb_class, label)

            end_labels.append(label)

        return end_labels

    def _symmetry_expand(self, comb_class, label):
        """Add symmetries of combinatorial class to the database."""
        if label not in self.symmetry_expanded:
            self.symmetry_expanded.add(label)
            for strategy_generator in self.symmetries:
                if isinstance(strategy_generator, Strategy):
                    strategies = [strategy_generator(comb_class, **self.kwargs)]
                elif isinstance(strategy_generator, StrategyGenerator):
                    strategies = strategy_generator(comb_class, **self.kwargs)
                for strategy in strategies:
                    rule = strategy(comb_class)
                    sym_label = self.classdb.get_label(rule.children[0])
                    self.ruledb.add(label, (sym_label,), rule)
                    self.classqueue.set_stop_yielding(sym_label)
                    self.symmetry_expanded.add(sym_label)

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
            if not self.ruledb.is_verified(label):
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
        status += "Total number of combinatorial classes found is {}\n".format(
            len(self.classdb.label_to_info)
        )

        status += "Total number of combinatorial rules is {}\n" "".format(
            len(self.ruledb.rule_to_strategy)
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
            specification = self.get_specification(smallest=smallest)

            if specification is not None:
                found_string = "Specification found {}\n".format(
                    time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
                )
                found_string += "Time taken was {} seconds\n\n".format(self._time_taken)
                # found_string += self.status()
                # found_string += json.dumps(specification.to_jsonable())
                logger.info(found_string, extra=self.logger_kwargs)
                # if kwargs.get("genf", False):
                #     min_poly, func = specification.get_min_poly(solve=True)
                #     return specification, min_poly, func
                return specification
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

    def get_specification(self, smallest: bool = False):
        try:
            if smallest:
                assert not self.iterative
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
