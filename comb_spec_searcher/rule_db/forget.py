"""
A database to search for tree.

The database do not store the strategy to save memory.
"""
import itertools
from typing import (
    TYPE_CHECKING,
    Iterable,
    Iterator,
    MutableMapping,
    Optional,
    Set,
    Tuple,
    Union,
    cast,
)

from comb_spec_searcher.class_db import ClassDB
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies.rule import AbstractRule
from comb_spec_searcher.strategies.strategy import AbstractStrategy, StrategyFactory
from comb_spec_searcher.strategies.strategy_pack import StrategyPack
from comb_spec_searcher.typing import RuleKey

from .base import RuleDBBase

if TYPE_CHECKING:
    from comb_spec_searcher import CombinatorialSpecificationSearcher

__all__ = ["RuleDBForgetStrategy"]


# pylint: disable=too-many-ancestors
class RecomputingDict(MutableMapping[RuleKey, AbstractStrategy]):
    """
    A mapping from rules to strategies that recompute the strategy every time it's
    needed instead of storing it in order to save memory.

    If only equiv is set to true the returned strategy will only create two way rules.

    Also in order to save memory we store flat version of the rules, i.e. for a rule
    (a, (b, c,...)) we store (a, b, c,...)
    """

    def __init__(
        self,
        only_equiv: bool,
    ) -> None:
        self._classdb: Optional[ClassDB] = None
        self._pack: Optional[StrategyPack] = None
        self.rules: Set[Tuple[int, ...]] = set()
        self.only_equiv: bool = only_equiv

    def link_searcher(self, classdb: ClassDB, strat_pack: StrategyPack) -> None:
        if self._classdb is not None or self._pack is not None:
            raise RuntimeError("Searcher is alreay linked")
        self._classdb = classdb
        self._pack = strat_pack

    @property
    def classdb(self) -> ClassDB:
        if self._classdb is None:
            raise RuntimeError("Not linked with classdb")
        return self._classdb

    @property
    def pack(self) -> StrategyPack:
        if self._pack is None:
            raise RuntimeError("Not linked with pack")
        return self._pack

    @staticmethod
    def _flatten(tuple_: RuleKey) -> Tuple[int, ...]:
        return (tuple_[0],) + tuple_[1]

    @staticmethod
    def _unflatten(tuple_: Tuple[int, ...]) -> RuleKey:
        return (tuple_[0], tuple_[1:])

    def __getitem__(self, key: RuleKey) -> AbstractStrategy:
        if self._flatten(key) not in self.rules:
            raise KeyError(key)
        possible_labels = (key[0],) + key[1]
        for label, strat in itertools.product(possible_labels, self.pack):
            comb_class = self.classdb.get_class(label)
            if isinstance(strat, StrategyFactory):
                strats_or_rules: Iterable[
                    Union[AbstractRule, AbstractStrategy]
                ] = strat(comb_class)
            else:
                strats_or_rules = [strat]
            for x in strats_or_rules:
                if isinstance(x, AbstractStrategy):
                    try:
                        rule = x(comb_class)
                    except StrategyDoesNotApply:
                        continue
                else:
                    rule = x
                try:
                    start_label = self.classdb.get_label(rule.comb_class)
                    nonempty_children = tuple(
                        c for c in rule.children if not self.classdb.is_empty(c)
                    )
                    end_labels = tuple(
                        sorted(map(self.classdb.get_label, nonempty_children))
                    )
                    if (start_label, end_labels) == key:
                        if self.only_equiv and not rule.is_two_way():
                            continue
                        return rule.strategy
                except StrategyDoesNotApply:
                    pass
        err_message = (
            f"Could not recompute the strategy for the rule {key} with "
            " any of the strategies. Classes are:\n"
        )
        for label in itertools.chain([key[0]], key[1]):
            err_message += f"Label: {label}\n"
            err_message += str(self.classdb.get_class(label)) + "\n"
        raise RuntimeError(err_message)

    def __setitem__(self, key: RuleKey, value: AbstractStrategy) -> None:
        assert not self.only_equiv or len(key[1]) == 1
        self.rules.add(self._flatten(key))

    def __delitem__(self, key: RuleKey) -> None:
        self.rules.remove(self._flatten(key))

    def __iter__(self) -> Iterator[RuleKey]:
        for rule in self.rules:
            yield self._unflatten(rule)

    def __len__(self) -> int:
        return len(self.rules)

    def __contains__(self, key: object) -> bool:
        return self._flatten(cast(RuleKey, key)) in self.rules


class RuleDBForgetStrategy(RuleDBBase):
    def __init__(self) -> None:
        super().__init__()
        self._rule_to_strategy = RecomputingDict(only_equiv=False)
        self._eqv_rule_to_strategy = RecomputingDict(only_equiv=True)

    def link_searcher(self, searcher: "CombinatorialSpecificationSearcher") -> None:
        super().link_searcher(searcher)
        classdb = searcher.classdb
        strat_pack = searcher.strategy_pack
        self.rule_to_strategy.link_searcher(classdb, strat_pack)
        self.eqv_rule_to_strategy.link_searcher(classdb, strat_pack)

    @property
    def rule_to_strategy(self) -> RecomputingDict:
        return self._rule_to_strategy

    @property
    def eqv_rule_to_strategy(self) -> RecomputingDict:
        return self._eqv_rule_to_strategy
