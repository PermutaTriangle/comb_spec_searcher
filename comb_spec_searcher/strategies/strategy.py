import abc
from importlib import import_module
from typing import Iterator, Optional, Tuple, TYPE_CHECKING, Union

from sympy import Eq, Function
from .constructor import Atom, CartesianProduct, Constructor, DisjointUnion, Empty
from .rule import Rule, VerificationRule
from ..combinatorial_class import CombinatorialClass, CombinatorialObject
from ..exception import InvalidOperationError, ObjectMappingError

if TYPE_CHECKING:
    from comb_spec_searcher import (
        CombinatorialSpecification,
        StrategyPack,
    )


__all__ = (
    "CartesianProductStrategy",
    "DisjointUnionStrategy",
    "Strategy",
    "StrategyGenerator",
    "SymmetryStrategy",
    "VerificationStrategy",
)


class Strategy(abc.ABC):
    """
    The Strategy method is essentially following the mantra of 'strategy' from the
    combinatorial explanation paper.
    (https://permutatriangle.github.io/papers/2019-02-27-combex.html)

    Having it as a class will give us more flexibility making it easier to
    implement sampling, object generation and future projects we've not
    thought of yet. It will also allow us to port over the code from Unnar's
    thesis in a more user-friendly manner.
    """

    def __init__(
        self,
        ignore_parent: bool = False,
        inferrable: bool = True,
        possibly_empty: bool = True,
        workable: bool = True,
    ):
        self._ignore_parent = ignore_parent
        self._inferrable = inferrable
        self._possibly_empty = possibly_empty
        self._workable = workable

    def __call__(
        self,
        comb_class: CombinatorialClass,
        children: Tuple[CombinatorialClass, ...] = None,
        **kwargs
    ) -> "Rule":
        if children is None:
            children = self.decomposition_function(comb_class)
        return Rule(self, comb_class, children=children)

    def to_revese_rule(
        self,
        comb_class: CombinatorialClass,
        children: Tuple[CombinatorialClass, ...] = None,
        **kwargs
    ) -> "Rule":
        if children is None:
            children = self.decomposition_function(comb_class)
        rule = Rule(self, comb_class, children=children)
        return rule.to_revese_rule(rule)

    @property
    def ignore_parent(self) -> bool:
        return self._ignore_parent

    @property
    def inferrable(self) -> bool:
        return self._inferrable

    @property
    def possibly_empty(self) -> bool:
        return self._possibly_empty

    @property
    def workable(self) -> bool:
        return self._workable

    @abc.abstractmethod
    def decomposition_function(
        self, comb_class: CombinatorialClass
    ) -> Tuple[CombinatorialClass, ...]:
        """
        Return the children of the strategy for the given comb_class. It
        should return None if it does not apply.
        """
        pass

    @abc.abstractmethod
    def constructor(
        self,
        comb_class: CombinatorialClass,
        children: Optional[Tuple[CombinatorialClass, ...]] = None,
    ) -> Constructor:
        """
        This is where the details of the 'reliance profile' and 'counting'
        functions are hidden.
        """
        if children is None:
            children = self.decomposition_function(comb_class)

    @abc.abstractmethod
    def formal_step(self) -> str:
        pass

    @abc.abstractmethod
    def backward_map(
        self,
        comb_class: CombinatorialClass,
        objs: Tuple[CombinatorialObject, ...],
        children: Optional[Tuple[CombinatorialObject, ...]] = None,
    ) -> CombinatorialObject:
        """This method will enable us to generate objects, and sample. """
        if children is None:
            children = self.decomposition_function(comb_class)

    @abc.abstractmethod
    def forward_map(
        self,
        comb_class: CombinatorialClass,
        obj: CombinatorialObject,
        children: Optional[Tuple[CombinatorialObject, ...]] = None,
    ) -> Tuple[CombinatorialObject, ...]:
        """This function will enable us to have a quick membership test."""
        if children is None:
            children = self.decomposition_function(comb_class)

    @abc.abstractmethod
    def __str__(self) -> str:
        """Return the name of the strategy."""

    @abc.abstractmethod
    def __repr__(self) -> str:
        pass


class CartesianProductStrategy(Strategy):
    def __init__(
        self,
        ignore_parent: bool = True,
        inferrable: bool = False,
        possibly_empty: bool = False,
        workable: bool = True,
    ):
        super().__init__(
            ignore_parent=ignore_parent,
            inferrable=inferrable,
            possibly_empty=possibly_empty,
            workable=workable,
        )

    def constructor(
        self,
        comb_class: CombinatorialClass,
        children: Optional[Tuple[CombinatorialClass, ...]] = None,
    ) -> Constructor:
        if children is None:
            children = self.decomposition_function(comb_class)
        return CartesianProduct(children)


class DisjointUnionStrategy(Strategy):
    def __init__(
        self,
        ignore_parent: bool = False,
        inferrable: bool = True,
        possibly_empty: bool = True,
        workable: bool = True,
    ):
        super().__init__(
            ignore_parent=ignore_parent,
            inferrable=inferrable,
            possibly_empty=possibly_empty,
            workable=workable,
        )

    def constructor(
        self,
        comb_class: CombinatorialClass,
        children: Optional[Tuple[CombinatorialClass, ...]] = None,
    ) -> Constructor:
        if children is None:
            children = self.decomposition_function(comb_class)
        return DisjointUnion(children)

    @staticmethod
    def backward_map_index(objs: Tuple[CombinatorialObject, ...],) -> int:
        for idx, obj in enumerate(objs):
            if isinstance(obj, CombinatorialObject):
                return idx
        raise ObjectMappingError(
            "For a disjoint union strategy, an object O is mapped to the tuple"
            "with entries being None, except at the index of the child which "
            "contains O, where it should be O."
        )

    @abc.abstractmethod
    def backward_map(
        self,
        comb_class: CombinatorialClass,
        objs: Tuple[CombinatorialObject, ...],
        children: Optional[Tuple[CombinatorialObject, ...]] = None,
    ) -> CombinatorialObject:
        """This method will enable us to generate objects, and sample.
        If it is a direct bijection, the below implementation will work!"""
        if children is None:
            children = self.decomposition_function(comb_class)
        return objs[DisjointUnionStrategy.backward_map_index(objs)]


class SymmetryStrategy(DisjointUnionStrategy):
    """General representation for a symmetry strategy."""

    def __init__(
        self,
        ignore_parent: bool = False,
        inferrable: bool = False,
        possibly_empty: bool = False,
        workable: bool = False,
    ):
        super().__init__(
            ignore_parent=ignore_parent,
            inferrable=inferrable,
            possibly_empty=possibly_empty,
            workable=workable,
        )


class VerificationStrategy(Strategy):
    """
    General representation of a strategy to enumerate combinatorial classes.
    """

    def __init__(
        self,
        ignore_parent: bool = True,
        inferrable: bool = True,
        possibly_empty: bool = True,
        workable: bool = True,
    ):
        super().__init__(
            ignore_parent=ignore_parent,
            inferrable=inferrable,
            possibly_empty=possibly_empty,
            workable=workable,
        )

    def __call__(
        self,
        comb_class: CombinatorialClass,
        children: Tuple[CombinatorialClass, ...] = None,
        **kwargs
    ) -> "Rule":
        if children is None:
            children = self.decomposition_function(comb_class)
        return VerificationRule(self, comb_class)

    @abc.abstractproperty
    def pack(self, comb_class: CombinatorialClass) -> "StrategyPack":
        """
        Returns a StrategyPack that finds a proof tree for the comb_class in
        which the verification strategies used are "simpler".

        The pack is assumed to produce a finite universe.
        """
        raise InvalidOperationError(
            "can't find specification for {}".format(self.__str__)
        )

    @abc.abstractmethod
    def verified(self, comb_class: CombinatorialClass) -> bool:
        """
        Returns True if enumeration strategy works for the combinatorial class.
        """

    def get_specification(
        self, comb_class: CombinatorialClass
    ) -> "CombinatorialSpecification":
        """
        Returns a combinatorial specification for the combinatorial class.
        Raises an `InvalidOperationError` if no specification can be found,
        e.g. if it is not verified.
        """
        if not self.verified(comb_class):
            raise InvalidOperationError("The combinatorial class is not verified")
        from ..comb_spec_searcher import CombinatorialSpecificationSearcher

        searcher = CombinatorialSpecificationSearcher(comb_class, self.pack(comb_class))
        specification = searcher.auto_search()
        if specification is None:
            raise InvalidOperationError("Cannot find a specification")
        return specification

    def get_genf(self, comb_class: CombinatorialClass):
        """
        Returns the generating function for the combinatorial class.
        Raises an InvalidOperationError if the combinatorial class is not verified.
        """
        if not self.verified(comb_class):
            raise InvalidOperationError("The combinatorial class is not verified")
        return self.get_specification(comb_class).get_genf()

    def decomposition_function(self, comb_class: CombinatorialClass) -> tuple:
        """
        A combinatorial class C is marked as verified by returning a rule
        C -> (). This ensures that C is in a combinatorial specification as it
        appears exactly once on the left hand side.

        The function returns None if the verification strategy doesn't apply.
        """
        if self.verified(comb_class):
            return tuple()
        return None

    def constructor(
        self,
        comb_class: CombinatorialClass,
        children: Optional[Tuple[CombinatorialClass, ...]] = None,
    ) -> Constructor:
        raise InvalidOperationError("No constructor on a verification strategy")

    def backward_map(
        self,
        comb_class: CombinatorialClass,
        objs: Tuple[CombinatorialObject, ...],
        children: Optional[Tuple[CombinatorialObject, ...]] = None,
    ) -> CombinatorialObject:
        raise InvalidOperationError("No backward map on a verification strategy")

    def forward_map(
        self,
        comb_class: CombinatorialClass,
        obj: CombinatorialObject,
        children: Optional[Tuple[CombinatorialObject, ...]] = None,
    ) -> Tuple[CombinatorialObject, ...]:
        raise InvalidOperationError("No backward map on a verification strategy")

    def count_objects_of_size(self, comb_class: CombinatorialClass, **parameters):
        """
        A  method to count the objects.
        Raises an InvalidOperationError if the combinatorial class is not verified.
        """
        if not self.verified(comb_class):
            raise InvalidOperationError("The combinatorial class is not verified")
        return self.get_specification(comb_class)

    def get_equation(self, comb_class: CombinatorialClass, lhs_func: Function,) -> Eq:
        return Eq(lhs_func, self.get_genf(comb_class))

    def generate_objects_of_size(
        self, comb_class: CombinatorialClass, **parameters
    ) -> Iterator[CombinatorialObject]:
        """
        A method to generate the objects.
        Raises an InvalidOperationError if the combinatorial class is not verified.
        """
        if not self.verified(comb_class):
            raise InvalidOperationError("The combinatorial class is not verified")
        return self.get_specification(comb_class).generate_objects_of_size(**parameters)


class EmptyStrategy(VerificationStrategy):
    def count_objects_of_size(self, comb_class: CombinatorialClass, **parameters):
        """Verification strategies must contain a method to count the objects."""
        return 0

    def get_genf(self, comb_class: CombinatorialClass):
        return 0

    def generate_objects_of_size(
        self, comb_class: CombinatorialClass, **parameters
    ) -> Iterator[CombinatorialObject]:
        """Verification strategies must contain a method to generate the objects."""
        return tuple()

    def verified(self, comb_class: CombinatorialClass):
        return comb_class.is_empty()

    def formal_step(self):
        return "is empty"

    def pack(self):
        raise InvalidOperationError("No pack for the empty strategy.")


STRATEGY_OUTPUT = Union[Optional[Strategy], Iterator[Strategy]]


class StrategyGenerator(abc.ABC):
    @abc.abstractmethod
    def __call__(self, comb_class: CombinatorialClass) -> STRATEGY_OUTPUT:
        """Returns the results of the strategy on a comb_class. This shou"""

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
