"""
An abstract class for a CombinatorialClass.
"""
import abc
from importlib import import_module
from typing import Any, Dict, Generic, Iterator, Tuple, Type, TypeVar

__all__ = ("CombinatorialClass", "CombinatorialObject")

CombinatorialObjectType = TypeVar(
    "CombinatorialObjectType", bound="CombinatorialObject"
)
CombinatorialClassType = TypeVar("CombinatorialClassType", bound="CombinatorialClass")


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

    def get_genf(self, *args, **kwargs) -> Any:
        """Return the generating function for the combinatorial class"""
        raise NotImplementedError(
            (
                "If you want to use the 'get_genf' function"
                "for a proof tree then you must implement"
                " 'get_genf' for verified combinatorial "
                "classes."
            )
        )

    def get_min_poly(self, *args, **kwargs) -> Any:
        """Return the minimum polynomial for the combinatorial class
        in terms of 'F'"""
        raise NotImplementedError(
            (
                "If you want to use the 'get_min_poly' "
                "function for a proof tree then you must "
                "implement 'get_genf' for verified "
                "combinatorial classes."
            )
        )

    @property
    def extra_parameters(self) -> Tuple[str, ...]:
        """
        Return a the parameters used to get the enumeration of the
        class. It is assumed we are always aware of 'n' which counts size.
        """
        return tuple()

    def possible_parameters(self, n: int) -> Iterator[Dict[str, int]]:
        """
        Return all the possible values the extra parameters could take for
        the given value of n.
        """
        yield dict()

    def objects_of_size(
        self, n: int, **parameters: int
    ) -> Iterator[CombinatorialObjectType]:
        """Returns an iterable of combinatorial objects of a given size."""
        raise NotImplementedError(
            "To use object generation and sampling with the AtomStrategy, this"
            "must be at least implemented for every class that is an atom."
        )

    def is_atom(self):
        """Returns True if the combinatorial class contains a single object."""
        raise NotImplementedError(
            "To use the CartesianProduct constructor, 'is_atom' and "
            "'minimum_size_of_object' must be implemented."
        )

    def minimum_size_of_object(self) -> int:
        """Return the size of the smallest object in the combinatorial class.
        Note, for productivity reasons, you must at least return 1, if this
        should be greater than 0. """
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
