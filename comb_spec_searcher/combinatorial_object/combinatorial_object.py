import sympy.abc

__all__ = ("CombinatorialObject")

class CombinatorialObject(object):
    """
    This is a base combinatorial object that CombinatorialSpecificationSearcher
    works with. Combintorial objects to be used with the searcher should
    inherhit from this class.
    """
    def get_genf(self, *args, **kwargs):
        print("I should return the generation function for the base CombinatorialObject of %s. Override me!" % self._get_class_name())
        return sympy.abc.x**0

    def objects_of_length(self, length):
        print("I should return an iterable")

    def to_jsonable(self):
        print("I should return a data structure that represents the object which is JSONable")

    def __init__(self):
        print("I'm the constructor for the base CombinatorialObject of %s. Override me!" % self._get_class_name())

    def __eq__(self, other):
        print("I'm the __eq__ function for the base CombinatorialObject of %s. Override me!" % self._get_class_name())

    def __hash__(self):
        print("I'm the __hash__ function for the base CombinatorialObject of %s. Override me!" % self._get_class_name())

    def __iter__(self):
        print("I'm the __iter__ function for the base CombinatorialObject of %s. Override me!" % self._get_class_name())

    def __repr__(self):
        print("I'm the __repr__ function for the base CombinatorialObject of %s. Override me!" % self._get_class_name())

    def __str__(self):
        print("I'm the __str__ function for the base CombinatorialObject of %s. Override me!" % self._get_class_name())

    def _get_class_name(self):
        return type(self).__name__