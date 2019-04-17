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
    def is_empty(self, *args, **kwargs):
        """Return True if objects of length yield nothing for all lengths"""
        return False

    @abc.abstractmethod
    def to_jsonable(self):
        """Return JSONable data structure of the class (a dictionary)"""
        pass

    def get_genf(self, *args, **kwargs):
        """Return the generating function for the combinatorial class"""
        raise NotImplementedError(("If you want to use the 'get_genf' function"
                                   "for a proof tree then you must implement"
                                   " 'get_genf' for verified combinatorial "
                                   "classes."))

    def get_min_poly(self, *args, **kwargs):
        """Return the minimim polynomial for the combinatorial class
        in terms of 'F'"""
        raise NotImplementedError(("If you want to use the 'get_min_poly' "
                                   "function for a proof tree then you must "
                                   "implement 'get_genf' for verified "
                                   "combinatorial classes."))

    def objects_of_length(self, length):
        """Returns an iterable of combinatorial objects of a given length"""
        raise NotImplementedError("This function needs to be added to your "
                                  "combinatorial class in order to use the "
                                  "debug settings and for initial conditions"
                                  " for computing the generating function")

    def from_dict(self):
        """Return combinatorial class from the jsonable object."""
        raise NotImplementedError("This function is need to reinstantiate a "
                                  "combinatorial class.")

    def compress(self):
        """Return a compressed version of the class. If you are having memory
        issues then implement this function and the decompress function such
        that 'cls.decompress(self.compress()) == self'"""
        return self

    @classmethod
    def decompress(cls, compressed):
        """Return decompressed class from string by compress function. If you
        are having memory issues then implement this function and the compress
        function such that 'cls.decompress(self.compress()) == self'"""
        return compressed

    @abc.abstractmethod
    def __init__(self):
        return

    @abc.abstractmethod
    def __eq__(self, other):
        return False

    @abc.abstractmethod
    def __hash__(self):
        pass

    @abc.abstractmethod
    def __repr__(self):
        pass

    @abc.abstractmethod
    def __str__(self):
        pass

    def _get_class_name(self):
        return type(self).__name__
