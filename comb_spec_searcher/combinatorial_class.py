"""
An abstract class for a CombinatorialClass.
"""
from importlib import import_module
from typing import Any, Iterator, TYPE_CHECKING
import abc

if TYPE_CHECKING:
    from typing import Type


__all__ = ("CombinatorialClass", "CombinatorialObject")


class CombinatorialObject(abc.ABC):
    """Abstract class for a combinatorial object."""

    @abc.abstractmethod
    def __len__(self) -> int:
        pass

    def size(self) -> int:
        """Return the size of the object"""
        return len(self)


class CombinatorialClass(abc.ABC):
    """
    Base class for CombSpecSearcher combinatorial class

    This is a base combinatorial class that CombinatorialSpecificationSearcher
    works with. Combinatorial classes to be used with the searcher should
    inherit from this class.
    """

    @abc.abstractmethod
    def is_empty(self, *args, **kwargs) -> bool:
        """Return True if there are no object of any lengths."""
        return False

    @abc.abstractclassmethod
    def from_dict(cls, d: dict) -> "CombinatorialClass":
        """Return the combinatorial class from the json dict representation."""
        module = import_module(d["class_module"])
        StratClass = getattr(
            module, d["comb_class"]
        )  # type: Type[CombinatorialClass] # noqa: E501
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

    def objects_of_size(self, size: int) -> Iterator[CombinatorialObject]:
        """Returns an iterable of combinatorial objects of a given length"""
        raise NotImplementedError(
            "This function needs to be added to your "
            "combinatorial class in order to use the "
            "debug settings and for initial conditions"
            " for computing the generating function"
        )

    def is_epsilon(self) -> bool:
        """Returns True if the generating function equals 1"""
        raise NotImplementedError(
            "If you want to use the "
            "'count_objects_of_length' function "
            "for a proof tree then you must implement "
            "'is_epsilon' for your combinatorial class."
        )

    def is_atom(self) -> bool:
        """Returns True if the generating function equals x"""
        raise NotImplementedError(
            "If you want to use the "
            "'count_objects_of_length' function "
            "for a proof tree then you must implement "
            "'is_epsilon', 'is_atom' and 'is_positive' "
            "for your combinatorial class."
        )

    def is_positive(self) -> bool:
        """Returns True if the constant term of the generating function is 0"""
        raise NotImplementedError(
            "If you want to use the "
            "'count_objects_of_length' function "
            "for a proof tree then you must implement "
            "'is_epsilon', 'is_atom' and 'is_positive' "
            "for your combinatorial class."
        )

    def to_bytes(self) -> bytes:
        """Return a compressed version of the class in the form of a 'bytes'
        object. If you are having memory issues then implement this function
        and the from_bytes function such that
        'cls.from_bytes(self.to_bytes()) == self'"""
        raise NotImplementedError

    @classmethod
    def from_bytes(cls, b: bytes) -> "CombinatorialClass":
        """Return decompressed class from the bytes object returned by the
        'to_bytes' function. If you are having memory issues then implement
        this function and the to_bytes function such that
        'cls.from_bytes(self.to_bytes()) == self'"""
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
