"""
Definition of the base feature of any ruledb.
"""
import abc
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Iterator,
    Optional,
    Tuple,
    TypeVar,
    cast,
)

from comb_spec_searcher.class_db import ClassDB
from comb_spec_searcher.exception import SpecificationNotFound
from comb_spec_searcher.strategies.rule import AbstractRule
from comb_spec_searcher.strategies.strategy_pack import StrategyPack

if TYPE_CHECKING:
    from comb_spec_searcher import CombinatorialSpecificationSearcher

RuleDBMethod = TypeVar("RuleDBMethod", bound=Callable[..., Any])


__all__ = ["ensure_specification", "RuleDBAbstract"]


class RuleDBAbstract(abc.ABC):
    NOT_LINK_ERROR = RuntimeError(
        "RuleDB is not linked with the searcher. Call `link_searcher` before using it."
    )

    def __init__(self) -> None:
        self._searcher: Optional["CombinatorialSpecificationSearcher"] = None

    def link_searcher(self, searcher: "CombinatorialSpecificationSearcher") -> None:
        if self._searcher is not None:
            raise RuntimeError("Searcher is alreay linked")
        self._searcher = searcher

    @property
    def searcher(self) -> "CombinatorialSpecificationSearcher":
        if self._searcher is None:
            raise RuleDBAbstract.NOT_LINK_ERROR
        return self._searcher

    @property
    def classdb(self) -> ClassDB:
        return self.searcher.classdb

    @property
    def strategy_pack(self) -> StrategyPack:
        from tilings.tilescope import OddOrEvenStrategy

        return self.searcher.strategy_pack.add_initial(OddOrEvenStrategy())

    @property
    def root_label(self) -> int:
        return self.searcher.start_label

    @abc.abstractmethod
    def is_verified(self, label: int) -> bool:
        """Return True if label has been verified."""

    @abc.abstractmethod
    def add(self, start: int, ends: Tuple[int, ...], rule: AbstractRule) -> None:
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


def ensure_specification(func: RuleDBMethod) -> RuleDBMethod:
    def inner(ruledb: RuleDBAbstract, *args, **kwargs):
        assert isinstance(ruledb, RuleDBAbstract)
        if not ruledb.has_specification():
            raise SpecificationNotFound
        return func(ruledb, *args, **kwargs)

    return cast(RuleDBMethod, inner)
