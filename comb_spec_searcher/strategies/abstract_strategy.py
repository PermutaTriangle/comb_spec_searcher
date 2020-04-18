import abc
from importlib import import_module
from typing import Iterator, Optional, Type, Union

from ..combinatorial_class import CombinatorialClass
from .rule import Rule

STRATEGY_OUTPUT = Union[Optional[Rule], Iterator[Rule]]


class Strategy(abc.ABC):
    @abc.abstractmethod
    def __call__(self, comb_class: CombinatorialClass, **kwargs) -> STRATEGY_OUTPUT:
        """Returns the results of the strategy on a comb_class."""

    @abc.abstractmethod
    def __str__(self) -> str:
        """Return the name of the strategy."""

    @abc.abstractmethod
    def __repr__(self) -> str:
        pass

    def __eq__(self, other: object) -> bool:
        return self.__class__ == other.__class__ and self.__dict__ == other.__dict__

    def __hash__(self):
        """
        Hash function for the strategy.

        As we don't expect a use case were many object for the same class
        strategy are used. This hash function should perform correctly.

        # TODO: do better, why is it hashable at all?
        """
        return hash(self.__class__)

    def to_jsonable(self) -> dict:
        """Return a dictionary form of the strategy."""
        c = self.__class__
        return {
            "class_module": c.__module__,
            "strategy_class": c.__name__,
        }

    @classmethod
    @abc.abstractmethod
    def from_dict(cls, d: dict) -> "Strategy":
        """Return the strategy from the json representation."""
        module = import_module(d.pop("class_module"))
        StratClass = getattr(
            module, d.pop("strategy_class")
        )  # type: Type[Strategy] # noqa: E501
        assert issubclass(StratClass, Strategy), "Not a valid strategy"
        return StratClass.from_dict(d)  # type: ignore
