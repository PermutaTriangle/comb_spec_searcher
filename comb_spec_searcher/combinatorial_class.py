"""
An abstract class for a CombinatorialClass.
"""
import abc
from functools import reduce
from importlib import import_module
from operator import mul
from typing import Counter, DefaultDict, Dict, Generic, Iterator, List, Tuple, Type

from sympy import Expr, Number, var

from comb_spec_searcher.typing import (
    CombinatorialClassType,
    CombinatorialObjectType,
    Objects,
    Parameters,
    Terms,
)

__all__ = ("CombinatorialClass", "CombinatorialObject")


class CombinatorialObject(abc.ABC):
    """Abstract class for a combinatorial object."""

    @abc.abstractmethod
    def __len__(self) -> int:
        pass

    def size(self) -> int:
        """Return the size of the object"""
        return len(self)


class CombinatorialClass(Generic[CombinatorialObjectType], abc.ABC):
    """
    Base class for CombSpecSearcher combinatorial class

    This is a base combinatorial class that CombinatorialSpecificationSearcher
    works with. Combinatorial classes to be used with the searcher should
    inherit from this class.
    """

    @abc.abstractmethod
    def is_empty(self) -> bool:
        """Return True if there are no object of any lengths."""
        return False

    @classmethod
    @abc.abstractmethod
    def from_dict(cls, d: dict) -> "CombinatorialClass":
        """Return the combinatorial class from the json dict representation."""
        module = import_module(d["class_module"])
        StratClass: Type["CombinatorialClass"] = getattr(module, d["comb_class"])
        assert issubclass(
            StratClass, CombinatorialClass
        ), "Not a valid CombinatorialClass"
        return StratClass.from_dict(d)  # type: ignore

    def to_jsonable(self) -> dict:
        """Return a dictionary form of the combinatorial class."""
        c = self.__class__
        return {
            "class_module": c.__module__,
            "comb_class": c.__name__,
        }

    def get_genf(self, *args, **kwargs) -> Expr:
        """Return the generating function for the combinatorial class"""
        raise NotImplementedError(
            (
                "If you want to use the 'get_genf' function"
                "for a proof tree then you must implement"
                " 'get_genf' for verified combinatorial "
                "classes."
            )
        )

    @property
    def extra_parameters(self) -> Tuple[str, ...]:
        """
        Return the parameters used to get the enumeration of the
        class. It is assumed that the order is consistent for a combinatorial class.
        """
        return tuple()

    def get_minimum_value(self, parameter: str) -> int:
        """
        Return the minimum value that can be taken by the parameter. This is
        required to be implemented if to use CartesianProduct on multiple
        variables.
        """
        raise NotImplementedError(
            "You need to implement the minimum value a parameter can take on "
            "your CombinatorialClass to use the CartesianProduct constructor."
        )

    def possible_parameters(self, n: int) -> Iterator[Dict[str, int]]:
        """
        Return all the possible values the extra parameters could take for
        the given value of n.
        """
        if self.extra_parameters:
            raise NotImplementedError(
                "You need to implement the possible parameters on your "
                "CombinatorialClass in order to use various methods, including "
                "sanity checking."
            )
        yield dict()

    def get_parameters(self, obj: CombinatorialObjectType) -> Parameters:
        """
        Returns the appropriate parameter tuple of the given object.
        """
        if self.extra_parameters:
            raise NotImplementedError(
                "You need to implement this method for combclass with extra parameters"
            )
        return tuple()

    def objects_of_size(
        self, n: int, **parameters: int
    ) -> Iterator[CombinatorialObjectType]:
        """
        Returns an iterable of combinatorial objects of a given size.

        If the combinatorial class has extra parameters and None are given, the iterator
        should go over all objects of size n.
        """
        raise NotImplementedError

    def get_terms(self, n: int) -> Terms:
        terms: Terms = Counter()
        for obj in self.objects_of_size(n):
            param = self.get_parameters(obj)
            terms[param] += 1
        return terms

    def get_objects(self, n: int) -> Objects:
        objects: Objects = DefaultDict(list)
        for obj in self.objects_of_size(n):
            param = self.get_parameters(obj)
            objects[param].append(obj)  # pylint: disable=invalid-sequence-index
        return objects

    def initial_conditions(self, check: int = 6) -> List[Expr]:
        """
        Returns a list with the initial conditions to size `check` of the
        CombinatorialClass.
        """

        def monomial(parameters: Dict[str, int]) -> Expr:
            return reduce(
                mul, [var(k) ** val for k, val in parameters.items()], Number(1)
            )

        return [
            sum(
                sum(Number(1) for _ in self.objects_of_size(n, **parameters))
                * monomial(parameters)
                for parameters in self.possible_parameters(n)
            )
            for n in range(check + 1)
        ]

    def is_atom(self):
        """Returns True if the combinatorial class contains a single object."""
        raise NotImplementedError(
            "To use the CartesianProduct constructor, 'is_atom' and "
            "'minimum_size_of_object' must be implemented."
        )

    def minimum_size_of_object(self) -> int:
        """Return the size of the smallest object in the combinatorial class.
        Note, for productivity reasons, you must at least return 1, if this
        should be greater than 0."""
        raise NotImplementedError(
            "To use the CartesianProduct constructor, 'is_atom' and "
            "'minimum_size_of_object' must be implemented."
        )

    def to_bytes(self) -> bytes:
        """Return a compressed version of the class in the form of a 'bytes'
        object. If you are having memory issues then implement this function
        and the from_bytes function such that
        'cls.from_bytes(self.to_bytes()) == self'"""
        raise NotImplementedError

    def to_html_representation(self) -> str:
        """Returns a string containing html representation for this class"""
        raise NotImplementedError("Use string method instead")

    @classmethod
    def from_bytes(
        cls: Type[CombinatorialClassType], b: bytes
    ) -> CombinatorialClassType:
        """
        Return decompressed class from the bytes object returned by the
        'to_bytes' function. If you are having memory issues then implement
        this function and the to_bytes function such that
        'cls.from_bytes(self.to_bytes()) == self'
        """
        raise NotImplementedError

    @abc.abstractmethod
    def __init__(self):
        return

    @abc.abstractmethod
    def __eq__(self, other) -> bool:
        return False

    @abc.abstractmethod
    def __hash__(self) -> int:
        pass

    @abc.abstractmethod
    def __repr__(self) -> str:
        pass

    @abc.abstractmethod
    def __str__(self) -> str:
        pass

    def _get_class_name(self) -> str:
        """Return the name of the class."""
        return type(self).__name__
