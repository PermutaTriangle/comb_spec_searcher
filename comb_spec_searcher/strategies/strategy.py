"""
The Strategy class is essentially following the mantra of 'strategy' from the
combinatorial explanation paper.
(https://permutatriangle.github.io/papers/2019-02-27-combex.html)

In order to use CombinatorialSpecificationSearcher, you must implement a
Strategy. The functions required are:
    - decomposition_function:   Given a combinatorial class, the decomposition
                                function should return the tuple of
                                combinatorial classes it can be counted by. The
                                function should return None if it doesn't
                                apply.
    - constructor:              Return a Constructor class. If you wish to use
                                CartesianProduct or DisjointUnion, consider
                                using the CartesianProductStrategy or
                                DisjointUnionStrategy subclasses.
    - formal_step:              A short string explaining what was done.
    - backward_map:             This is the backward mapping of the underlying
                                bijection of the strategy. If you want to
                                generate objects, or sample you must implement
                                this. You can instead raise NotImplementedError
                                if you don't wish to use these features.
    - forward_map:              This is the forward mapping of the underlying
                                bijection. See the discussion for forward map.
    - __repr__ and __str__:     This is mostly for printing purposes!
    - from_dict:                A method that can recreate the class. The dict
                                passed is empty. If your strategy needs extra
                                parameters to recreate you should overwrite the
                                to_jsonable method.
Also included in this file is a StrategyFactory class. This is useful if you
are defining a family of strategies. When the __call__ method is applied to it,
it should return an iterator of Strategy to try and apply to the comb_class.

For a VerificationStrategy you must implement the methods:
    - verified:                 Return True if the combinatorial class is
                                verified by the strategy.
    - pack                      The pack is used to count and generate the
                                objects. If the strategy doesn't have a CSS
                                strategy pack that can be used to enumerate
                                verified combinatorial classes, then you need
                                to implement the methods get_terms,
                                get_objects, and get_genf.
    - __repr__ and __str__:     This is mostly for printing purposes!
    - from_dict:                A method that can recreate the class. The dict
                                passed is empty. If your strategy needs extra
                                parameters to recreate you should overwrite the
                                to_jsonable method.
If your verification strategy is for the atoms, consider using the
AtomStrategy, relying on CombinatorialClass methods.
"""
import abc
from collections import defaultdict
from importlib import import_module
from typing import (
    TYPE_CHECKING,
    Counter,
    Dict,
    Generic,
    Iterator,
    Optional,
    Tuple,
    Type,
    Union,
    cast,
)

from sympy import Expr, Function, Integer, var

from comb_spec_searcher.typing import CSSstrategy, Objects, Terms

from ..combinatorial_class import (
    CombinatorialClass,
    CombinatorialClassType,
    CombinatorialObject,
    CombinatorialObjectType,
)
from ..exception import InvalidOperationError, ObjectMappingError, StrategyDoesNotApply
from .constructor import CartesianProduct, Constructor, DisjointUnion
from .rule import AbstractRule, Rule, VerificationRule

if TYPE_CHECKING:
    from comb_spec_searcher import CombinatorialSpecification

    from .strategy_pack import StrategyPack

__all__ = (
    "AbstractStrategy",
    "CartesianProductStrategy",
    "DisjointUnionStrategy",
    "Strategy",
    "StrategyFactory",
    "SymmetryStrategy",
    "VerificationStrategy",
)


def strategy_from_dict(d) -> CSSstrategy:
    """
    Return the AbstractStrategy or StrategyFactory from the json representation.
    """
    module = import_module(d.pop("class_module"))
    StratClass: Type[CSSstrategy] = getattr(module, d.pop("strategy_class"))
    assert issubclass(
        StratClass, (AbstractStrategy, StrategyFactory)
    ), "Not a valid strategy"
    return StratClass.from_dict(d)


class AbstractStrategy(
    abc.ABC, Generic[CombinatorialClassType, CombinatorialObjectType]
):
    """
    A base class for strategies for methods that Strategy and
    VerificationStrategy have in common.
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

    @abc.abstractmethod
    def __call__(
        self,
        comb_class: CombinatorialClassType,
        children: Tuple[CombinatorialClassType, ...] = None,
        **kwargs,
    ) -> AbstractRule[CombinatorialClassType, CombinatorialObjectType]:
        """
        Return the rule formed by using the strategy.
        """

    @property
    def ignore_parent(self) -> bool:
        """
        Return True if it is not worth expanding the parent/comb_class if
        the strategy applies.
        """
        return self._ignore_parent

    @property
    def inferrable(self) -> bool:
        """
        Return True if the children could change using inferral strategies.
        """
        return self._inferrable

    @property
    def possibly_empty(self) -> bool:
        """
        Return True if it is possible that a child is empty.
        """
        return self._possibly_empty

    @property
    def workable(self) -> bool:
        """
        Return True if the children can expanded using other strategies.
        """
        return self._workable

    @abc.abstractmethod
    def can_be_equivalent(self) -> bool:
        """
        Return True if every Rule returned with one non-empty child is an
        equivalence rule.
        """

    @abc.abstractmethod
    def decomposition_function(
        self, comb_class: CombinatorialClassType
    ) -> Optional[Tuple[CombinatorialClassType, ...]]:
        """
        Return the children of the strategy for the given comb_class. It
        should return None if it does not apply.
        """

    @abc.abstractmethod
    def formal_step(self) -> str:
        """
        Return a short string to explain what the strategy has done.
        """

    @staticmethod
    def get_eq_symbol() -> str:
        """
        Return a choice for '=' in the pretty print a '=' b '?' c of rules.
        Your choice should be a single charachter.
        """
        return "="

    @staticmethod
    def get_op_symbol() -> str:
        """
        Return a choice for '?' in the pretty print a '=' b '?' c of rules.
        Your choice should be a single charachter.
        """
        return "?"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AbstractStrategy):
            return NotImplemented
        return self.__class__ == other.__class__ and self.__dict__ == other.__dict__

    def __repr__(self):
        return (
            self.__class__.__name__
            + f"(ignore_parent={self.ignore_parent}, inferrable={self.inferrable},"
            f" possibly_empty={self.possibly_empty}, workable={self.workable})"
        )

    def __str__(self) -> str:
        return self.formal_step()

    def to_jsonable(self) -> dict:
        """
        Return a dictionary form of the strategy.
        """
        c = self.__class__
        return {
            "class_module": c.__module__,
            "strategy_class": c.__name__,
            "ignore_parent": self._ignore_parent,
            "inferrable": self._inferrable,
            "possibly_empty": self._possibly_empty,
            "workable": self._workable,
        }

    @classmethod
    @abc.abstractmethod
    def from_dict(cls, d: dict) -> CSSstrategy:
        return strategy_from_dict(d)


class Strategy(AbstractStrategy[CombinatorialClassType, CombinatorialObjectType]):
    """
    The Strategy class is essentially following the mantra of 'strategy' from the
    combinatorial explanation paper.
    (https://permutatriangle.github.io/papers/2019-02-27-combex.html)

    In order to use CombinatorialSpecificationSearcher, you must implement a
    Strategy. The functions required are:
        - decomposition_function:   Given a combinatorial class, the decomposition
                                    function should return the tuple of
                                    combinatorial classes it can be counted by. The
                                    function should return None if it doesn't
                                    apply.
        - constructor:              Return a Constructor class. If you wish to use
                                    CartesianProduct or DisjointUnion, consider
                                    using the CartesianProductStrategy or
                                    DisjointUnionStrategy subclasses.
        - formal_step:              A short string explaining what was done.
        - backward_map:             This is the backward mapping of the underlying
                                    bijection of the strategy. If you want to
                                    generate objects, or sample you must implement
                                    this. You can instead raise NotImplementedError
                                    if you don't wish to use these features.
        - forward_map:              This is the forward mapping of the underlying
                                    bijection. See the discussion for forward map.
        - __repr__ and __str__:     This is mostly for printing purposes!
        - from_dict:                A method that can recreate the class. The dict
                                    passed is empty. If your strategy needs extra
                                    parameters to recreate you should overwrite the
                                    to_jsonable method.
    """

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

    def __call__(
        self,
        comb_class: CombinatorialClassType,
        children: Tuple[CombinatorialClassType, ...] = None,
        **kwargs,
    ) -> Rule[CombinatorialClassType, CombinatorialObjectType]:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        return Rule(self, comb_class, children=children)

    @abc.abstractmethod
    def constructor(
        self,
        comb_class: CombinatorialClassType,
        children: Optional[Tuple[CombinatorialClassType, ...]] = None,
    ) -> Constructor:
        """
        This is where the details of the 'reliance profile' and 'counting'
        functions are hidden.
        """
        if children is None:
            children = self.decomposition_function(comb_class)

    @abc.abstractmethod
    def backward_map(
        self,
        comb_class: CombinatorialClassType,
        objs: Tuple[Optional[CombinatorialObjectType], ...],
        children: Optional[Tuple[CombinatorialClassType, ...]] = None,
    ) -> Iterator[CombinatorialObjectType]:
        """
        The backward direction of the underlying bijection used for object
        generation and sampling.
        """
        if children is None:
            children = self.decomposition_function(comb_class)

    @abc.abstractmethod
    def forward_map(
        self,
        comb_class: CombinatorialClassType,
        obj: CombinatorialObjectType,
        children: Optional[Tuple[CombinatorialClassType, ...]] = None,
    ) -> Tuple[Optional[CombinatorialObjectType], ...]:
        """
        The forward direction of the underlying bijection used for object
        generation and sampling.
        """
        if children is None:
            children = self.decomposition_function(comb_class)

    def extra_parameters(
        self,
        comb_class: CombinatorialClassType,
        children: Optional[Tuple[CombinatorialClassType, ...]] = None,
    ) -> Tuple[Dict[str, str], ...]:
        """
        This should be a tuple of dictionaries where the parent parameters point
        to the corresponding child parameter. Any parent parameter not
        corresponding to a child parameter must have no objects that are on
        that child.
        """
        assert not comb_class.extra_parameters, (
            "you need to update the 'extra_parameters' method in the strategy {} "
            "in order to enumerate class with multiple extra_parameters".format(
                str(self)
            )
        )
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        return tuple(dict() for _ in children)


class CartesianProductStrategy(
    Strategy[CombinatorialClassType, CombinatorialObjectType]
):
    """
    The CartesianProductStrategy is a subclass of strategy. The constructor is
    CartesianProduct. Such strategies by default assume
    ignore_parent=True, inferrable=False, possibly_empty=False, and
    workable=True.

    The bijection maps an object a -> (b1, ..., bk) where bi is the object in
    the child at index i returned by the decomposition function.
    """

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

    @staticmethod
    def can_be_equivalent() -> bool:
        return True

    def constructor(
        self,
        comb_class: CombinatorialClassType,
        children: Optional[Tuple[CombinatorialClassType, ...]] = None,
    ) -> Constructor:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        return CartesianProduct(
            comb_class,
            children,
            extra_parameters=self.extra_parameters(comb_class, children),
        )

    @staticmethod
    def get_op_symbol() -> str:
        """
        Return a choice for 'x' in the pretty print a '=' b 'x' c of rules.
        Your choice should be a single charachter.
        """
        return "x"


class DisjointUnionStrategy(Strategy[CombinatorialClassType, CombinatorialObjectType]):
    """
    The DisjointUnionStrategy is a subclass of Strategy. The constructor used
    is DisjointUnion.

    The bijection maps an object a -> (None, ..., b, ..., None) where b is at
    the index of the child it belongs to.
    """

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

    @staticmethod
    def can_be_equivalent() -> bool:
        return True

    def constructor(
        self,
        comb_class: CombinatorialClassType,
        children: Optional[Tuple[CombinatorialClassType, ...]] = None,
    ) -> DisjointUnion:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        return DisjointUnion(
            comb_class,
            children,
            extra_parameters=self.extra_parameters(comb_class, children),
        )

    @staticmethod
    def backward_map_index(objs: Tuple[Optional[CombinatorialObjectType], ...]) -> int:
        """
        Return the index of the comb_class that the sub_object returned.
        """
        for idx, obj in enumerate(objs):
            if obj is not None:
                return idx
        raise ObjectMappingError(
            "For a disjoint union strategy, an object O is mapped to the tuple"
            "with entries being None, except at the index of the child which "
            "contains O, where it should be O."
        )

    def backward_map(
        self,
        comb_class: CombinatorialClassType,
        objs: Tuple[Optional[CombinatorialObjectType], ...],
        children: Optional[Tuple[CombinatorialClassType, ...]] = None,
    ) -> Iterator[CombinatorialObjectType]:
        """
        This method will enable us to generate objects, and sample.
        If it is a direct bijection, the below implementation will work!
        """
        if children is None:
            children = self.decomposition_function(comb_class)
        idx = DisjointUnionStrategy.backward_map_index(objs)
        yield cast(CombinatorialObjectType, objs[idx])

    @staticmethod
    def get_op_symbol() -> str:
        """
        Return a choice for '+' in the pretty print a '=' b '+' c of rules.
        Your choice should be a single charachter.
        """
        return "+"


class SymmetryStrategy(
    DisjointUnionStrategy[CombinatorialClassType, CombinatorialObjectType]
):
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


class VerificationStrategy(
    AbstractStrategy[CombinatorialClassType, CombinatorialObjectType]
):
    """
    For a VerificationStrategy you must implement the methods:
        - verified:                 Return True if the combinatorial class is
                                    verified by the strategy.
        - pack                      The pack is used to count and generate the
                                    objects. If the strategy doesn't have a CSS
                                    strategy pack that can be used to enumerate
                                    verified combinatorial classes, then you need
                                    to implement the methods get_terms,
                                    get_objects, and get_genf.
        - __repr__ and __str__:     This is mostly for printing purposes!
        - from_dict:                A method that can recreate the class. The dict
                                    passed is empty. If your strategy needs extra
                                    parameters to recreate you should overwrite the
                                    to_jsonable method.
    If your verification strategy is for the atoms, consider using the
    AtomStrategy, relying on CombinatorialClass methods.
    """

    def __init__(self, ignore_parent: bool = True):
        super().__init__(
            ignore_parent=ignore_parent,
            inferrable=False,
            possibly_empty=False,
            workable=False,
        )

    def __call__(
        self,
        comb_class: CombinatorialClassType,
        children: Tuple[CombinatorialClassType, ...] = None,
        **kwargs,
    ) -> VerificationRule[CombinatorialClassType, CombinatorialObjectType]:
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("The combinatorial class is not verified")
        return VerificationRule(self, comb_class, children)

    @staticmethod
    def can_be_equivalent() -> bool:
        return False

    def pack(self, comb_class: CombinatorialClassType) -> "StrategyPack":
        """
        Returns a StrategyPack that finds a proof tree for the comb_class in
        which the verification strategies used are "simpler".

        The pack is assumed to produce a finite universe.
        """
        raise InvalidOperationError(f"can't find specification for {self}")

    @abc.abstractmethod
    def verified(self, comb_class: CombinatorialClassType) -> bool:
        """
        Returns True if enumeration strategy works for the combinatorial class.
        """

    def get_specification(
        self, comb_class: CombinatorialClassType
    ) -> "CombinatorialSpecification[CombinatorialClassType, CombinatorialObjectType]":
        """
        Returns a combinatorial specification for the combinatorial class.
        Raises an `StrategyDoesNotApply` if no specification can be found,
        e.g. if it is not verified.
        """
        if not self.verified(comb_class):
            raise StrategyDoesNotApply("The combinatorial class is not verified")
        # pylint: disable=import-outside-toplevel
        from ..comb_spec_searcher import CombinatorialSpecificationSearcher

        searcher = CombinatorialSpecificationSearcher(comb_class, self.pack(comb_class))
        specification = searcher.auto_search()
        assert specification is not None, StrategyDoesNotApply(
            "Cannot find a specification"
        )
        return specification

    def get_genf(
        self,
        comb_class: CombinatorialClassType,
        funcs: Optional[Dict[CombinatorialClassType, Function]] = None,
    ) -> Expr:
        """
        Returns the generating function for the combinatorial class.
        Raises an StrategyDoesNotApply if the combinatorial class is not verified.
        """
        if not self.verified(comb_class):
            raise StrategyDoesNotApply("The combinatorial class is not verified")
        return self.get_specification(comb_class).get_genf()

    def decomposition_function(
        self, comb_class: CombinatorialClassType
    ) -> Union[Tuple[CombinatorialClassType, ...], None]:
        """
        A combinatorial class C is marked as verified by returning a rule
        C -> (). This ensures that C is in a combinatorial specification as it
        appears exactly once on the left hand side.

        The function returns None if the verification strategy doesn't apply.
        """
        if self.verified(comb_class):
            return tuple()
        return None

    def get_terms(self, comb_class: CombinatorialClassType, n: int) -> Terms:
        """
        Return the terms for n given the subterms of the children.
        """
        if not self.verified(comb_class):
            raise StrategyDoesNotApply("The combinatorial class is not verified")
        return self.get_specification(comb_class).get_terms(n)

    def get_objects(self, comb_class: CombinatorialClassType, n: int) -> Objects:
        """
        A method to get all the objects of a given size n partitioned by parameters.
        Raises an StrategyDoesNotApply if the combinatorial class is not verified.
        """
        if not self.verified(comb_class):
            raise StrategyDoesNotApply("The combinatorial class is not verified")
        return self.get_specification(comb_class).get_objects(n)

    def random_sample_object_of_size(
        self, comb_class: CombinatorialClassType, n: int, **parameters: int
    ) -> CombinatorialObjectType:
        """
        A method to sample uniformly at random from a verified combinatorial class.
        Raises an StrategyDoesNotApply if the combinatorial class is not verified.
        """
        if not self.verified(comb_class):
            raise StrategyDoesNotApply("The combinatorial class is not verified")
        return self.get_specification(comb_class).random_sample_object_of_size(
            n, **parameters
        )

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d.pop("inferrable")
        d.pop("possibly_empty")
        d.pop("workable")
        return d


class AtomStrategy(VerificationStrategy[CombinatorialClass, CombinatorialObject]):
    """
    A subclass for when a combinatorial class is an atom - meaning consisting
    of a single object.
    """

    def __init__(self):
        super().__init__(ignore_parent=True)

    @staticmethod
    def get_terms(comb_class: CombinatorialClass, n: int) -> Terms:
        if comb_class.extra_parameters:
            raise NotImplementedError
        if n == comb_class.minimum_size_of_object():
            return Counter([tuple()])
        return Counter()

    @staticmethod
    def get_objects(comb_class: CombinatorialClass, n: int) -> Objects:
        if comb_class.extra_parameters:
            raise NotImplementedError
        res: Objects = defaultdict(list)
        if n == comb_class.minimum_size_of_object():
            res[tuple()].append(next(comb_class.objects_of_size(n)))
        return res

    def get_genf(
        self,
        comb_class: CombinatorialClass,
        funcs: Optional[Dict[CombinatorialClass, Function]] = None,
    ) -> Expr:
        if comb_class.extra_parameters:
            raise NotImplementedError
        if not self.verified(comb_class):
            raise StrategyDoesNotApply("Can't find generating functon for non-atom.")
        x = var("x")
        return x ** comb_class.minimum_size_of_object()

    @staticmethod
    def random_sample_object_of_size(
        comb_class: CombinatorialClass, n: int, **parameters: int
    ) -> CombinatorialObject:
        if comb_class.extra_parameters:
            raise NotImplementedError
        if n == comb_class.minimum_size_of_object():
            obj: CombinatorialObject = next(comb_class.objects_of_size(n))
            return obj

    @staticmethod
    def verified(comb_class: CombinatorialClass) -> bool:
        return bool(comb_class.is_atom())

    @staticmethod
    def formal_step() -> str:
        return "is atom"

    @staticmethod
    def pack(comb_class: CombinatorialClass) -> "StrategyPack":
        raise InvalidOperationError("No pack for the empty strategy.")

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d.pop("ignore_parent")
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "AtomStrategy":
        assert not d
        return cls()

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"(ignore_parent={self.ignore_parent})"

    def __str__(self) -> str:
        return "verify atoms"


class EmptyStrategy(VerificationStrategy[CombinatorialClass, CombinatorialObject]):
    """
    A subclass for when a combinatorial class is equal to the empty set.
    """

    def __init__(self):
        super().__init__(ignore_parent=True)

    @staticmethod
    def get_terms(comb_class: CombinatorialClass, n: int) -> Terms:
        return Counter()

    @staticmethod
    def get_objects(comb_class: CombinatorialClass, n: int) -> Objects:
        return defaultdict(list)

    def get_genf(
        self,
        comb_class: CombinatorialClass,
        funcs: Optional[Dict[CombinatorialClass, Function]] = None,
    ) -> Integer:
        if not self.verified(comb_class):
            raise StrategyDoesNotApply(
                "can't find generating functon for non-empty class."
            )
        return Integer(0)

    @staticmethod
    def random_sample_object_of_size(
        comb_class: CombinatorialClass, n: int, **parameters: int
    ) -> CombinatorialObject:
        raise StrategyDoesNotApply("Can't sample from empty set.")

    @staticmethod
    def verified(comb_class: CombinatorialClass) -> bool:
        return bool(comb_class.is_empty())

    @staticmethod
    def formal_step() -> str:
        return "is empty"

    @staticmethod
    def pack(comb_class: CombinatorialClass) -> "StrategyPack":
        raise InvalidOperationError("No pack for the empty strategy.")

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d.pop("ignore_parent")
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "EmptyStrategy":
        assert not d
        return cls()

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    def __str__(self) -> str:
        return "the empty strategy"


class StrategyFactory(abc.ABC, Generic[CombinatorialClassType]):
    """
    The StrategyFactory class can be used instead of the Strategy class if
    you wish to expand a combinatorial class with a family of strategies.
    """

    @abc.abstractmethod
    def __call__(
        self, comb_class: CombinatorialClassType, **kwargs
    ) -> Iterator[Union[AbstractRule, AbstractStrategy]]:
        """
        Returns the results of the strategy on a comb_class.
        """

    @abc.abstractmethod
    def __str__(self) -> str:
        """
        Return the name of the strategy.
        """

    @abc.abstractmethod
    def __repr__(self) -> str:
        pass

    def __eq__(self, other: object) -> bool:
        return self.__class__ == other.__class__ and self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        """
        Hash function for the strategy.

        As we don't expect a use case were many object for the same class
        strategy are used. This hash function should perform correctly.

        # TODO: do better, why is it hashable at all?
        """
        return hash(self.__class__)

    def to_jsonable(self) -> dict:
        """
        Return a dictionary form of the strategy.
        """
        c = self.__class__
        return {
            "class_module": c.__module__,
            "strategy_class": c.__name__,
        }

    @classmethod
    @abc.abstractmethod
    def from_dict(cls, d: dict) -> CSSstrategy:
        """
        Return the strategy from the json representation.
        """
        return strategy_from_dict(d)
