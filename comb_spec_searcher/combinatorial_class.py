import abc
import sympy.abc

__all__ = ("CombinatorialClass")


class CombinatorialClass(abc.ABC):
    """
    Base class for CombSpecSearcher combinatorial class

    This is a base combinatorial class that CombinatorialSpecificationSearcher
    works with. Combintorial classes to be used with the searcher should
    inherhit from this class.
    """

    @abc.abstractmethod
    def get_genf(self, *args, **kwargs):
        """Return True if objects of length returns nothing for all lengths"""
        return False

    @abc.abstractmethod
    def get_genf(self, *args, **kwargs):
        """Return the generating function for the combinatorial object"""
        return sympy.abc.x**0

    @abc.abstractmethod
    def objects_of_length(self, length):
        """Returns an iterable of combinatorial objects of a given length"""
        return []

    @abc.abstractmethod
    def to_jsonable(self):
        """Return JSONable data structure of the object"""
        return

    @abc.abstractmethod
    def __init__(self):
        return

    @abc.abstractmethod
    def __eq__(self, other):
        return False

    @abc.abstractmethod
    def __hash__(self):
        return

    @abc.abstractmethod
    def __repr__(self):
        return

    @abc.abstractmethod
    def __str__(self):
        return

    def _get_class_name(self):
        return type(self).__name__
