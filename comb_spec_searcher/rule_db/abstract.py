"""
Definition of the base feature of any ruledb.
"""
import abc
from typing import Any, Callable, Iterator, Optional, Tuple, TypeVar, cast

from comb_spec_searcher.class_db import ClassDB
from comb_spec_searcher.exception import SpecificationNotFound
from comb_spec_searcher.strategies.rule import AbstractRule
from comb_spec_searcher.strategies.strategy_pack import StrategyPack

RuleDBMethod = TypeVar("RuleDBMethod", bound=Callable[..., Any])


__all__ = ["ensure_specification", "RuleDBAbstract"]


def ensure_specification(func: RuleDBMethod) -> RuleDBMethod:
    def inner(ruledb: RuleDBAbstract, *args, **kwargs):
        assert isinstance(ruledb, RuleDBAbstract)
        if not ruledb.has_specification():
            raise SpecificationNotFound
        return func(ruledb, *args, **kwargs)

    return cast(RuleDBMethod, inner)


class RuleDBAbstract(abc.ABC):
    NOT_LINK_ERROR = RuntimeError(
        "RuleDB is not linked with the searcher. Call `link_searcher` before using it."
    )

    def __init__(self) -> None:
        self._classdb: Optional[ClassDB] = None
        self._strategy_pack: Optional[StrategyPack] = None
        self._root_label: Optional[int] = None

    def link_searcher(
        self, root_label: int, classdb: ClassDB, strat_pack: StrategyPack
    ) -> None:
        if (
            self._root_label is not None
            or self._classdb is not None
            or self._strategy_pack is not None
        ):
            raise RuntimeError("Searcher is alreay linked")
        self._classdb = classdb
        self._strategy_pack = strat_pack
        self._root_label = root_label

    @property
    def classdb(self) -> ClassDB:
        if self._classdb is None:
            raise RuleDBAbstract.NOT_LINK_ERROR
        return self._classdb

    @property
    def strategy_pack(self) -> StrategyPack:
        if self._strategy_pack is None:
            raise RuleDBAbstract.NOT_LINK_ERROR
        return self._strategy_pack

    @property
    def root_label(self) -> int:
        if self._root_label is None:
            raise RuleDBAbstract.NOT_LINK_ERROR
        return self._root_label

    @abc.abstractmethod
    def is_verified(self, label: int) -> bool:
        """Return True if label has been verified."""

    @abc.abstractmethod
    def add(self, label: int, end_labels: Tuple[int, ...], rule: AbstractRule) -> None:
        """
        Add a rule to the database.

        - start is a single integer.
        - ends is a tuple of integers, representing the children.
        - rule is a Rule that creates start -> ends.
        """

    @abc.abstractmethod
    def status(self, elaborate: bool) -> str:
        """Return a string describing the status of the rule database."""

    @abc.abstractmethod
    def has_specification(self) -> bool:
        """Indicate if the rule db contains a specification for the given label."""

    @abc.abstractmethod
    def get_specification_rules(self, **kwargs) -> Iterator[AbstractRule]:
        """
        Return the rules that constitute a specification.

        Raise a SpecificationNotFound error if the ruledb does not contain a
        specification.

        The kwargs should to used to pass some option for the specification search that
        are specific to each type of ruledb.
        """
