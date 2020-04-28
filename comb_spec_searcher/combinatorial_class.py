from typing import Any, Iterator

import abc

__all__ = ("CombinatorialClass", "CombinatorialObject")


class CombinatorialObject(abc.ABC):
    @abc.abstractmethod
    def __len__(self) -> int:
        pass

    def size(self) -> int:
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

    @abc.abstractmethod
    def to_jsonable(self):
        """Return JSONable data structure of the class (a dictionary)"""

    def get_genf(self, *args, **kwargs):
        """Return the generating function for the combinatorial class"""
        raise NotImplementedError(
            (
                "If you want to use the 'get_genf' function"
                "for a proof tree then you must implement"
                " 'get_genf' for verified combinatorial "
                "classes."
            )
        )

    def get_min_poly(self, *args, **kwargs):
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

    @classmethod
    def from_dict(cls, dictionary: dict) -> "CombinatorialClass":
        """Return combinatorial class from the jsonable object."""
        raise NotImplementedError(
            "This function is need to reinstantiate a combinatorial class."
        )

    def from_parts(self, *args, **kwargs) -> CombinatorialObject:
        """Return the object created from the parts given by a cartesian rule
        applied on the comb_class. This is required for random sampling. The
        formal step will be passed as the kwarg 'formal_step'."""
        raise NotImplementedError(
            "This function is needed to perform random" " sampling."
        )

    def compress(self) -> Any:
        """Return a compressed version of the class. If you are having memory
        issues then implement this function and the decompress function such
        that 'cls.decompress(self.compress()) == self'"""
        return self

    @classmethod
    def decompress(cls, compressed: Any) -> "CombinatorialClass":
        """Return decompressed class from string by compress function. If you
        are having memory issues then implement this function and the compress
        function such that 'cls.decompress(self.compress()) == self'"""
        return compressed

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
        return type(self).__name__
