"""
A database for rules.
"""
from itertools import product
from typing import Iterable, Iterator, List, MutableMapping, Set, Tuple, Union, cast

from comb_spec_searcher.class_db import ClassDB
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies import Rule
from comb_spec_searcher.strategies.rule import AbstractRule
from comb_spec_searcher.strategies.strategy import AbstractStrategy, StrategyFactory
from comb_spec_searcher.strategies.strategy_pack import StrategyPack

from .base import RuleDBBase

__all__ = ["RuleDBForgetStrategy"]

Specification = Tuple[List[Tuple[int, AbstractStrategy]], List[List[int]]]
RuleKey = Tuple[int, Tuple[int, ...]]


class RecomputingDict(MutableMapping[RuleKey, AbstractStrategy]):
    """
    A mapping from rules to strategies that recompute the strategy every time it's
    needed instead of storing it in order to save memory.

    Also in order to save memory we store flat version of the rules, i.e. for a rule
    (a, (b, c,...)) we store (a, b, c,...)
    """

    def __init__(self, classdb: ClassDB, strat_pack: StrategyPack) -> None:
        self.classdb = classdb
        self.pack = strat_pack
        self.rules: Set[Tuple[int, ...]] = set()

    @staticmethod
    def _flatten(tuple_: RuleKey) -> Tuple[int, ...]:
        return (tuple_[0],) + tuple_[1]

    @staticmethod
    def _unflatten(tuple_: Tuple[int, ...]) -> RuleKey:
        return (tuple_[0], tuple_[1:])

    def __getitem__(self, key: RuleKey) -> AbstractStrategy:
        if self._flatten(key) not in self.rules:
            raise KeyError(key)
        possible_comb_classes = tuple(map(self.classdb.get_class, (key[0],) + key[1]))
        for comb_class, strat in product(possible_comb_classes, self.pack):
            if isinstance(strat, StrategyFactory):
                strats_or_rules: Iterable[Union[Rule, AbstractStrategy]] = strat(
                    comb_class
                )
            else:
                strats_or_rules = [strat]
            rules: Iterator[AbstractRule] = (
                x(comb_class) if isinstance(x, AbstractStrategy) else x
                for x in strats_or_rules
            )
            for rule in rules:
                try:
                    nonempty_children = tuple(
                        c for c in rule.children if not self.classdb.is_empty(c)
                    )
                    end_labels = tuple(
                        sorted(map(self.classdb.get_label, nonempty_children))
                    )
                    if end_labels == key[1]:
                        return rule.strategy
                except StrategyDoesNotApply:
                    pass
        err_message = (
            f"Could not recompute the strategy for the rule {key} with "
            " any of the strategies"
        )
        raise RuntimeError(err_message)

    def __setitem__(self, key: RuleKey, value: AbstractStrategy) -> None:
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
    def __init__(self, classdb: ClassDB, strat_pack: StrategyPack) -> None:
        super().__init__()
        self.rules = RecomputingDict(classdb, strat_pack)

    @property
    def rule_to_strategy(self):
        return self.rules
