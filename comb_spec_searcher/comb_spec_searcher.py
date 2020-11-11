"""A class for automatically performing combinatorial exploration."""
import gc
import logging
import platform
import time
import warnings
from collections import defaultdict
from datetime import timedelta
from typing import (
    Any,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
    cast,
)

import logzero
import tabulate
from logzero import logger
from sympy import Eq, Function, var

from comb_spec_searcher.typing import (
    CombinatorialClassType,
    CSSstrategy,
    SpecificationClassesAndStrats,
    WorkPacket,
)

from .class_db import ClassDB
from .class_queue import DefaultQueue
from .exception import (
    ExceededMaxtimeError,
    InvalidOperationError,
    SpecificationNotFound,
    StrategyDoesNotApply,
)
from .rule_db import RuleDB, RuleDBForgetStrategy
from .rule_db.base import RuleDBBase
from .specification import CombinatorialSpecification
from .strategies import (
    AbstractStrategy,
    StrategyFactory,
    StrategyPack,
    VerificationRule,
)
from .strategies.rule import AbstractRule
from .utils import (
    cssiteratortimer,
    cssmethodtimer,
    get_mem,
    nice_pypy_mem,
    size_to_readable,
)

if platform.python_implementation() == "CPython":
    from pympler.asizeof import asizeof

__all__ = ["CombinatorialSpecificationSearcher"]

warnings.simplefilter("once", Warning)

logzero.loglevel(logging.INFO)


class CombinatorialSpecificationSearcher(Generic[CombinatorialClassType]):
    """
    The CombinatorialSpecificationSearcher class.

    This is used to build up knowledge about a combinatorial_class with respect
    to the given strategies and search for a combinatorial specification.
    """

    def __init__(
        self,
        start_class: CombinatorialClassType,
        strategy_pack: StrategyPack,
        ruledb: Optional[Union[str, RuleDB]] = None,
        **kwargs,
    ):
        """
        Initialise CombinatorialSpecificationSearcher.

        OTHER INPUT:
            - `ruledb`: a string to specify the type of ruledb to use for the
            search. Default to `None` but can be changed to "forget" for a ruledb that
            saves more memory.
            - `expand_verified`: if True, every verified combinatorial class will
              still be expanded using the strategies in strategy pack
            - `debug`: if True every rule found will be sanity checked and logged
              to logging.DEBUG
            - `function_kwargs` are passed to the call method of strategies
        """
        self.strategy_pack = strategy_pack
        self.debug = kwargs.get("debug", False)
        self.expand_verified = kwargs.get("expand_verified", False)
        if self.debug:
            logzero.loglevel(logging.DEBUG, True)
        self.kwargs = kwargs.get("function_kwargs", dict())

        self.func_times: Dict[str, float] = defaultdict(float)
        self.func_calls: Dict[str, int] = defaultdict(int)

        self.kwargs["symmetry"] = bool(strategy_pack.symmetries)

        self.classdb = ClassDB[CombinatorialClassType](type(start_class))
        self.classqueue = DefaultQueue(strategy_pack)

        if ruledb is None:
            self.ruledb: RuleDBBase = RuleDB()
        elif ruledb == "forget":
            self.ruledb = RuleDBForgetStrategy(self.classdb, self.strategy_pack)
        elif isinstance(ruledb, RuleDBBase):
            self.ruledb = ruledb
        else:
            raise ValueError(
                "ruledb argument should be None or 'forget' or a RuleDB object"
            )

        # initialise the run with start_class
        self.start_label = self.classdb.get_label(start_class)
        self._add_to_queue(self.start_label)
        self.tried_to_verify: Set[int] = set()
        self.symmetry_expanded: Set[int] = set()
        self.try_verify(start_class, self.start_label)
        if self.symmetries:
            self._symmetry_expand(start_class, self.start_label)

    @property
    def verification_strategies(self) -> Sequence[CSSstrategy]:
        """The verification strategies from the strategy pack."""
        return self.strategy_pack.ver_strats

    @property
    def iterative(self) -> bool:
        """The iterative parameter from the strategy pack."""
        return self.strategy_pack.iterative

    @property
    def symmetries(self) -> Sequence[CSSstrategy]:
        """The symmetries functions for the strategy pack."""
        return self.strategy_pack.symmetries

    def try_verify(self, comb_class: CombinatorialClassType, label: int) -> None:
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
    def is_empty(self, comb_class: CombinatorialClassType, label: int) -> bool:
        """Return True if a combinatorial class contains no objects, False
        otherwise."""
        empty = self.classdb.is_empty(comb_class, label)
        return empty

    def _expand(
        self,
        comb_class: CombinatorialClassType,
        label: int,
        strategies: Tuple[CSSstrategy, ...],
        inferral: bool,
    ) -> None:
        """
        Will expand the combinatorial class with given label using the given
        strategies.
        """
        if inferral:
            self._inferral_expand(comb_class, label, strategies)
        else:
            for strategy_generator in strategies:
                for start_label, end_labels, rule in self._expand_class_with_strategy(
                    comb_class, strategy_generator, label
                ):
                    self._add_rule(start_label, end_labels, rule)

    def _rules_from_strategy(
        self, comb_class: CombinatorialClassType, strategy: CSSstrategy
    ) -> Iterator[AbstractRule]:
        """Yield all the rules given by a strategy/strategy generator."""
        if isinstance(strategy, AbstractStrategy):
            try:
                yield strategy(comb_class, **self.kwargs)
            except StrategyDoesNotApply:
                pass
        elif isinstance(strategy, StrategyFactory):
            for strat in strategy(comb_class, **self.kwargs):
                if isinstance(strat, AbstractRule):
                    yield strat
                elif isinstance(strat, AbstractStrategy):
                    try:
                        yield strat(comb_class, **self.kwargs)
                    except StrategyDoesNotApply:
                        continue
                else:
                    raise InvalidOperationError(
                        "Attempting to add non Rule type. A Strategy "
                        "Generator's __call__ method should yield Strategy or "
                        "Strategy(comb_class, children) object."
                    )
        else:
            raise InvalidOperationError(
                "CSS can only expand a combinatorial class with "
                "Strategy and StrategyFactory"
            )

    @cssiteratortimer("_expand_class_with_strategy")
    def _expand_class_with_strategy(
        self,
        comb_class: CombinatorialClassType,
        strategy_generator: CSSstrategy,
        label: Optional[int] = None,
        initial: bool = False,
    ) -> Iterator[Tuple[int, Tuple[int, ...], AbstractRule]]:
        """
        Will expand the class with given strategy. Return time taken.
        """
        logger.debug(
            "Expanding label %s with %s",
            label,
            strategy_generator,
        )
        if label is None:
            label = self.classdb.get_label(comb_class)

        for rule in self._rules_from_strategy(comb_class, strategy_generator):
            try:
                children = rule.children
            except StrategyDoesNotApply:
                continue
            if len(children) == 1 and rule.comb_class == children[0]:
                logger.debug(
                    "The equivalence strategy %s returned the same "
                    "combinatorial class when applied to %r",
                    str(rule).split(" ")[1],
                    comb_class,
                )
                continue
            end_labels = [self.classdb.get_label(child) for child in children]
            if rule.comb_class == comb_class:
                start_label = label
            else:
                start_label = self.classdb.get_label(rule.comb_class)

            # TODO: observe that creating this constructor could be costly,
            # e.g. Cartesian
            if self.debug:
                logger.debug(
                    "Adding combinatorial rule %s -> %s\n%s",
                    start_label,
                    tuple(end_labels),
                    rule,
                )
                try:
                    n = 4
                    for i in range(n + 1):
                        rule.sanity_check(n=i)
                    logger.debug("Sanity checked rule to length %s.", n)
                except NotImplementedError as e:
                    logger.debug(
                        "Could not sanity check rule due to:\n"
                        "NotImplementedError: %s",
                        e,
                    )
            if any(
                self.ruledb.are_equivalent(start_label, elabel) for elabel in end_labels
            ):
                # This says comb_class = comb_class, so we skip it, but mark
                # every other class as empty.
                for elabel in end_labels:
                    if not self.ruledb.are_equivalent(start_label, elabel):
                        self._add_empty_rule(elabel)
                if self.debug:
                    for elabel, child in zip(end_labels, children):
                        if not self.ruledb.are_equivalent(start_label, elabel):
                            assert child.is_empty()

            yield start_label, tuple(end_labels), rule

    def _add_rule(
        self, start_label: int, end_labels: Tuple[int, ...], rule: AbstractRule
    ) -> None:
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
                logger.debug("Label %s is empty.", child_label)
                continue
            if rule.workable:
                self._add_to_queue(child_label)
            if not rule.inferrable:
                self._not_inferrable(child_label)
            if not rule.possibly_empty:
                self.classdb.set_empty(child_label, empty=False)

            self.try_verify(comb_class, child_label)

            cleaned_end_labels.append(child_label)

        if cleaned_end_labels == [start_label]:
            return

        if rule.ignore_parent:
            self._stop_yielding(start_label)

        if not cleaned_end_labels:
            # this must be a verification strategy!
            assert isinstance(rule, VerificationRule), rule.formal_step
        self.ruledb.add(start_label, tuple(cleaned_end_labels), rule)

    def _add_empty_rule(self, label: int) -> None:
        """Mark label as empty. Treated as verified as can count empty set."""
        self.classdb.set_empty(label, empty=True)

    def _symmetry_expand(self, comb_class: CombinatorialClassType, label: int) -> None:
        """Add symmetries of combinatorial class to the database."""
        sym_labels = set([label])
        for strategy_generator in self.symmetries:
            for start_label, end_labels, rule in self._expand_class_with_strategy(
                comb_class, strategy_generator, label=label
            ):
                sym_label = end_labels[0]
                self.ruledb.add(start_label, (sym_label,), rule)
                self._stop_yielding(sym_label)
                sym_labels.add(sym_label)
        self.symmetry_expanded.update(sym_labels)

    def _inferral_expand(
        self,
        comb_class: CombinatorialClassType,
        label: int,
        inferral_strategies: Tuple[CSSstrategy, ...],
        skip: Optional[CSSstrategy] = None,
    ):
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
                self._not_inferrable(start_label)
                inferral_strategies = (
                    inferral_strategies[i + 1 :] + inferral_strategies[0 : i + 1]
                )
                self._inferral_expand(
                    inf_class, inf_label, inferral_strategies, skip=strategy_generator
                )
                break
        self._not_inferrable(label)

    def get_equations(self, **kwargs) -> Set[Eq]:
        """
        Returns a set of equations for all rules currently found.
        """
        x = var("x")

        def get_function(comb_class):
            label = self.classdb.get_label(comb_class)
            eqv_label = self.ruledb.equivdb[label]
            return Function("F_{}".format(eqv_label))(x)

        eqs = set()
        for start, ends, strategy in self.ruledb.all_rules():
            parent = self.classdb.get_class(start)
            children = tuple(map(self.classdb.get_class, ends))
            rule = strategy(parent, children)
            try:
                eq = rule.get_equation(get_function)
            except NotImplementedError:
                logger.info(
                    "can't find generating function for %s." " The comb class is:\n%s",
                    get_function(rule.comb_class),
                    rule.comb_class,
                )
                eq = Eq(get_function(rule.comb_class), Function("NOTIMPLEMENTED")(x))
            eqs.add(eq)
        return eqs

    def do_level(self) -> None:
        """Expand combinatorial classes in current queue. Combintorial classes
        found added to next."""
        for label, strategies, inferral in self.classqueue.do_level():
            comb_class = self.classdb.get_class(label)
            self._expand(comb_class, label, strategies, inferral)

    def _labels_to_expand(self) -> Iterator[WorkPacket]:
        yield from self.classqueue

    def _add_to_queue(self, label: int):
        self.classqueue.add(label)

    def _not_inferrable(self, label: int):
        self.classqueue.set_not_inferrable(label)

    def _stop_yielding(self, label: int):
        self.classqueue.set_stop_yielding(label)

    @cssmethodtimer("status")
    def status(self, elaborate: bool) -> str:
        """
        Return a string of the current status of the CombSpecSearcher.

        It includes:
        - number of combinatorial classes, and information about verification
        - the times spent in each of the main functions

        "elaborate" status updates are those that provide information that
        may be slow to compute
        """
        status = "CSS status:\n"
        total = sum(self.func_times.values())
        status += f"\tTotal time accounted for: {timedelta(seconds=int(total))}\n"
        status += self._css_status(total)
        status += self.classdb.status() + "\n"
        status += self.classqueue.status() + "\n"
        status += self.ruledb.status(elaborate) + "\n"
        status += self.mem_status(elaborate)
        return status

    @cssmethodtimer("status")
    def _css_status(self, total: float) -> str:
        table: List[Tuple[str, str, timedelta, str]] = []
        for explanation in self.func_calls:
            count = f"{self.func_calls[explanation]:,d}"
            time_spent = timedelta(seconds=int(self.func_times[explanation]))
            if total == 0:
                percentage = "? %"
            else:
                percentage = f"{int((self.func_times[explanation] * 100) / total)}%"
            table.append((explanation, count, time_spent, percentage))
        table.sort(key=lambda row: row[2], reverse=True)
        headers = ["", "Number of \napplications", "\nTime spent", "\nPercentage"]
        colalign = ("left", "right", "right", "right")
        return (
            "    "
            + tabulate.tabulate(table, headers=headers, colalign=colalign).replace(
                "\n", "\n    "
            )
            + "\n"
        )

    @cssmethodtimer("status")
    def mem_status(self, elaborate: bool) -> str:
        """Provide status information related to memory usage."""

        status = "Memory Status:\n"
        table: List[Tuple[str, str]] = []
        table.append(("OS Allocated", size_to_readable(get_mem())))
        if platform.python_implementation() == "CPython":
            # Warning: "asizeof" can be very slow!
            if elaborate:
                table.append(("CSS", size_to_readable(asizeof(self))))
                table.append(("ClassDB", size_to_readable(asizeof(self.classdb))))
                table.append(("ClassQueue", size_to_readable(asizeof(self.classqueue))))
                table.append(("RuleDB", size_to_readable(asizeof(self.ruledb))))

        elif platform.python_implementation() == "PyPy":
            gc_stats = cast(Any, gc.get_stats())
            stats = [
                ("Current Memory Used", gc_stats.total_gc_memory),
                ("Current Memory Allocated", gc_stats.total_allocated_memory),
                ("Current JIT Memory Used", gc_stats.jit_backend_used),
                ("Current JIT Memory Allocated", gc_stats.jit_backend_allocated),
                ("Peak Memory Used", gc_stats.peak_memory),
                ("Peak Memory Allocated Memory Used", gc_stats.peak_allocated_memory),
            ]
            for (desc, mem) in stats:
                table.append((desc, nice_pypy_mem(mem)))
        status += "    "
        status += tabulate.tabulate(table, colalign=("left", "right")).replace(
            "\n", "\n    "
        )
        status += "\n"
        if platform.python_implementation() == "PyPy":
            status += "\tTotal Garbage Collection Time: {}\n".format(
                timedelta(seconds=int(gc_stats.total_gc_time / 1000))
            )
        return status

    def run_information(self) -> str:
        """Return string detailing what CombSpecSearcher is looking for."""
        start_string = (
            "Initialising CombSpecSearcher for the combinatorial"
            " class:\n{}\n".format(self.classdb.get_class(self.start_label))
        )
        start_string += str(self.strategy_pack)
        return start_string

    def _log_spec_found(
        self, specification: CombinatorialSpecification, start_time: float
    ):
        found_string = "Specification built {}\n".format(
            time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
        )
        time_taken = time.time() - start_time
        found_string += f"Time taken: {timedelta(seconds=int(time_taken))}\n"
        found_string += self.status(elaborate=True)
        found_string += (
            f"Specification found has {specification.number_of_rules()} rules"
        )
        logger.info(found_string)

    def _log_status(self, start_time: float, status_update: int) -> None:
        time_taken = time.time() - start_time
        status = f"Time taken so far: {timedelta(seconds=int(time_taken))}\n"
        elaborate = time.time() - start_time > 100 * self.func_times["status"]
        status_start = time.time()
        status += self.status(elaborate=elaborate)
        ne_goal = 100 * self.func_times["status"] - (time.time() - start_time)
        next_elaborate = round(ne_goal - (ne_goal % status_update) + status_update)
        if elaborate:
            status += " -- status update took {} seconds --\n".format(
                round(time.time() - status_start, 2)
            )
        else:
            status += (
                " -- next elaborate status update in "
                f"{timedelta(seconds=next_elaborate)} --\n"
            )
        logger.info(status)

    def auto_search(self, **kwargs) -> CombinatorialSpecification:
        """
        An automatic search function.

        Classes will be expanded until a proof tree is found. A tree will be
        searched for approximately 1% of the search time. This can be set using
        the 'perc' keyword, as some percentage between 0 and 100.

        The search will continue, unless a proof tree is found. You can set the
        keyword 'max_time' to stop the search after 'max_time' many seconds.
        If max_time is reached it will raise a ExceededMaxtimeError.

        Information is logged to logger.info. It will also log the proof tree,
        in json format. For periodic status_updates, set the keyword flag
        'status_update', an update will be given every status_update seconds.
        "Elaborate" status updates, which provide slow-to-calculate information
        will be given periodically, so that they take less than 1% of computation
        time.

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
            )
            perc = 1
        status_update = kwargs.get("status_update", None)
        max_time = kwargs.get("max_time", None)
        status_start = time.time()
        start_string = "Auto search started {}\n".format(
            time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
        )
        start_string += self.run_information()
        logger.info(start_string)

        max_expansion_time = 0
        expanding = True

        while expanding:
            expanding, status_start = self._expand_classes_for(
                max_expansion_time, status_update, status_start, auto_search_start
            )

            spec_search_start = time.time()
            logger.debug("Searching for specification.")
            specification = self.get_specification(
                smallest=kwargs.get("smallest", False),
                minimization_time_limit=0.01 * (time.time() - auto_search_start),
            )
            if specification is not None:
                self._log_spec_found(specification, auto_search_start)
                return specification
            logger.debug("No specification found.")
            if max_time is not None:
                if time.time() - auto_search_start > max_time:
                    raise ExceededMaxtimeError(
                        "Exceeded maximum time. Aborting auto search.",
                    )
            # worst case, search every hour
            multiplier = 100 // perc
            max_expansion_time = min(
                multiplier * (time.time() - spec_search_start), 3600
            )
            logger.debug(
                "Will expand for %s seconds.",
                round(max_expansion_time, 2),
            )

    def _auto_search_rules(self) -> SpecificationClassesAndStrats:
        """
        A basic auto search for returning equivalence paths and rules.

        This method is used by CombinatorialSpecification for expanding
        verified classes.

        Will raise SpecificationNotFound error if no specification is found
        after running out of classes to expand.
        """
        status_start = time.time()
        status_update = None  # this prevents status updates happening
        auto_search_start = time.time()
        max_expansion_time: float = 0
        expanding = True
        while expanding:
            expanding, status_start = self._expand_classes_for(
                max_expansion_time, status_update, status_start, auto_search_start
            )
            spec_search_start = time.time()
            spec = self._get_specification_rules(
                0.01 * (time.time() - auto_search_start)
            )
            if spec is not None:
                return spec
            max_expansion_time = min(0.01 * (time.time() - spec_search_start), 3600)
        raise SpecificationNotFound

    def _expand_classes_for(
        self,
        expansion_time: float,
        status_update: Optional[int],
        status_start: float,
        auto_search_start: float,
    ) -> Tuple[bool, float]:
        """
        Will expand classes for `expansion_time` seconds.

        It will return a pair (bool, time), where the bool is True if there are
        more classes to expand, False otherwise. The `time` is the initial time
        for checking whether to post a status update.
        """
        expansion_start = time.time()
        last_label = None
        expanding = True
        for label, strategies, inferral in self._labels_to_expand():
            if label != last_label:
                comb_class = self.classdb.get_class(label)
                last_label = label
            if self.expand_verified or not self.ruledb.is_verified(label):
                self._expand(comb_class, label, strategies, inferral)
            if time.time() - expansion_start > expansion_time:
                break
            if status_update is not None and time.time() - status_start > status_update:
                self._log_status(auto_search_start, status_update)
                status_start = time.time()
        else:
            expanding = False
            logger.info("No more classes to expand.")
        return expanding, status_start

    @cssmethodtimer("get specification")
    def get_specification(
        self, minimization_time_limit: float = 10, smallest: bool = False
    ) -> Optional[CombinatorialSpecification]:
        """
        Return a CombinatorialSpecification if the universe contains one.

        The minimization_time_limit only applies when smallest is false.

        The function will return None if no such CombinatorialSpecification
        exists in the universe.
        """
        spec = self._get_specification_rules(minimization_time_limit, smallest)
        if spec is None:
            return None
        start_class = self.classdb.get_class(self.start_label)
        strategies, comb_class_eqv_paths = spec
        logger.info("Creating a specification.")
        return CombinatorialSpecification(start_class, strategies, comb_class_eqv_paths)

    @cssmethodtimer("get specification")
    def _get_specification_rules(
        self, minimization_time_limit: float = 10, smallest: bool = False
    ) -> Optional[SpecificationClassesAndStrats]:
        """
        Returns the equivalence paths needed to create a
        CombinatorialSpecification, if one exists.

        The minimization_time_limit only applies when smallest is false.

        The function will return None if no such CombinatorialSpecification
        exists in the universe.
        """
        try:
            if smallest:
                if self.iterative:
                    raise InvalidOperationError("can't use iterative and smallest")
                rules, eqv_paths = self.ruledb.get_smallest_specification(
                    self.start_label
                )
            else:
                rules, eqv_paths = self.ruledb.get_specification_rules(
                    self.start_label,
                    minimization_time_limit=minimization_time_limit,
                    iterative=self.iterative,
                )
        except SpecificationNotFound:
            return None
        comb_class_eqv_paths = [
            list(map(self.classdb.get_class, path)) for path in eqv_paths
        ]
        strategies = [(self.classdb.get_class(label), rule) for label, rule in rules]
        return strategies, comb_class_eqv_paths
