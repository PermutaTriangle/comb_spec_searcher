Combinatorial Specification Searcher
====================================
.. image:: https://travis-ci.org/PermutaTriangle/comb_spec_searcher.svg?branch=master
    :alt: Travis
    :target: https://travis-ci.org/PermutaTriangle/comb_spec_searcher
.. image:: https://img.shields.io/coveralls/github/PermutaTriangle/comb_spec_searcher.svg
    :alt: Coveralls
    :target: https://coveralls.io/github/PermutaTriangle/comb_spec_searcher
.. image:: https://img.shields.io/pypi/v/comb_spec_searcher.svg
    :alt: PyPI
    :target: https://pypi.python.org/pypi/comb_spec_searcher
.. image:: https://img.shields.io/pypi/l/comb_spec_searcher.svg
    :target: https://pypi.python.org/pypi/comb_spec_searcher
.. image:: https://img.shields.io/pypi/pyversions/comb_spec_searcher.svg
    :target: https://pypi.python.org/pypi/comb_spec_searcher

.. image:: http://img.shields.io/badge/readme-tested-brightgreen.svg
    :alt: Travis
    :target: https://travis-ci.org/PermutaTriangle/comb_spec_searcher

.. image:: https://requires.io/github/PermutaTriangle/comb_spec_searcher/requirements.svg?branch=master
     :target: https://requires.io/github/PermutaTriangle/comb_spec_searcher/requirements/?branch=master
     :alt: Requirements Status

The ``comb_spec_searcher`` package contains code for combinatorial
exploration.

Installing
----------

To install ``comb_spec_searcher`` on your system, run:

.. code:: bash

       pip install comb_spec_searcher

It is also possible to install comb_spec_searcher in development mode to
work on the source code, in which case you run the following after
cloning the repository:

.. code:: bash

       ./setup.py develop

Combinatorial exploration
-------------------------

A (combinatorial) class is a set of objects with a notion of size such
that there are finitely many objects of each size. One of the primary
goals of enumerative combinatorics is to count how many objects of each
size there are in a class. One method for doing this is to find a
(combinatorial) specification, which is a collection of (combinatorial)
rules that describe how to build a class from other classes using
well-defined constructors. Such a specification can then be used to
count the number of objects of each size.

*Combinatorial exploration* is a systematic application of strategies to
create rules about a class of interest, until a specification can be
found. This package can be used to perform this process automatically.
See the `Combinatorial Exploration
project <https://permutatriangle.github.io/papers/2019-02-27-combex.html>`__
and `Christian Bean’s PhD
thesis <https://opinvisindi.is/handle/20.500.11815/1184>`__ for more details.

The remainder of this README will be an example of how to use this
package for performing combinatorial exploration on a specific class,
namely words avoiding consecutive patterns.

Avoiding consecutive patterns in words
--------------------------------------

A word ``w`` over an alphabet ``Σ`` is a string consisting of letters
from ``Σ``. We say that ``w`` contains the word ``p`` if there is a
consecutive sequence of letters in ``w`` equal to ``p``. We say ``w``
avoids ``p`` if it does not contain ``p``. In this context, we call
``p`` a pattern. In ``python``, this containment check can be checked
using ``in``.

.. code:: python

   >>> w = "acbabcabbb"
   >>> p = "abcab"
   >>> p in w
   True

For an alphabet ``Σ`` and a set of patterns ``P`` we define ``Σ*(P)`` to
be the set of words over ``Σ`` that avoid every pattern in ``P``. These
are the classes that we will count. Of course, these all form regular
languages, but it will serve as a good example of how to use the
``comb_spec_searcher`` package.

The first step is to create the classes that will be used for
discovering the underlying structure of the class of interest. In this
case, considering the prefix of the words is what we need. We then
create a new python ``class`` representing this that inherits from
``CombinatorialClass`` which can be imported from
``comb_spec_searcher``.

.. code:: python

   >>> from comb_spec_searcher import CombinatorialClass


   >>> class AvoidingWithPrefix(CombinatorialClass):
   ...     def __init__(self, prefix, patterns, alphabet, just_prefix=False):
   ...         self.alphabet = frozenset(alphabet)
   ...         self.prefix = prefix
   ...         self.patterns = frozenset(patterns)
   ...         self.just_prefix = just_prefix # this will be needed later

Inheriting from ``CombinatorialClass`` requires you to implement a few
functions for combinatorial exploration: ``is_empty``, ``to_jsonable``,
``__eq__``, ``__hash__``, ``__repr__``, and ``__str__``.

We will start by implementing the dunder methods (the ones with double
underscores) required. The ``__eq__`` method is particularly important
as the ``CombinatorialSpecificationSearcher`` will use it to recognise
if the same class appears multiple times.

.. code:: python

   ...     # The dunder methods required to perform combinatorial exploration
   ...
   ...     def __eq__(self, other):
   ...         return (self.alphabet == other.alphabet and
   ...                 self.prefix == other.prefix and
   ...                 self.patterns == other.patterns and
   ...                 self.just_prefix == other.just_prefix)
   ...
   ...     def __hash__(self):
   ...         return hash(hash(self.prefix) + hash(self.patterns) +
   ...                     hash(self.alphabet) + hash(self.just_prefix))
   ...
   ...     def __str__(self):
   ...         prefix = self.prefix if self.prefix else '""'
   ...         if self.just_prefix:
   ...             return "The word {}".format(prefix)
   ...         return ("Words over {{{}}} avoiding {{{}}} with prefix {}"
   ...                 "".format(", ".join(l for l in self.alphabet),
   ...                           ", ".join(p for p in self.patterns),
   ...                           prefix))
   ...
   ...     def __repr__(self):
   ...         return "AvoidingWithPrefix({}, {}, {}".format(repr(self.prefix),
   ...                                                       repr(self.patterns),
   ...                                                       repr(self.alphabet))

Perhaps the most important function to be implemented is the
``is_empty`` function. This should return ``True`` if there are no
objects of any size in the class, otherwise ``False``. If it is not
correctly implemented it may lead to tautological specifications. For
example, in our case the class is empty if and only if the prefix
contains a pattern to be avoided.

.. code:: python

   ...     def is_empty(self):
   ...         return any(p in self.prefix for p in self.patterns)

The final function required is ``to_jsonable``. This is primarily for
the output, and only necessary for saving the output. It should be in a
format that can be interpretated by ``json``. What is important is that
the ``from_dict`` function is written in such a way that for any class
``c`` we have ``CombinatorialClass.from_dict(c.to_jsonable()) == c``.

.. code:: python

   ...     def to_jsonable(self):
   ...         return {"prefix": self.prefix,
   ...                 "patterns": tuple(sorted(self.patterns)),
   ...                 "alphabet": tuple(sorted(self.alphabet)),
   ...                 "just_prefix": int(self.just_prefix)}
   ...
   ...     @classmethod
   ...     def from_dict(cls, data):
   ...         return cls(data['prefix'],
   ...                    data['patterns'],
   ...                    data['alphabet'],
   ...                    bool(int(data['just_prefix'])))

We also add some methods that we will need to get the enumerations of the
objects later.

.. code:: python

   ...     def is_atom(self):
   ...        """Return True if the class contains a single word."""
   ...        return self.just_prefix
   ...
   ...     def minimum_size_of_object(self):
   ...        """Return the size of the smallest object in the class."""
   ...        return len(self.prefix)

Our ``CombinatorialClass`` is now ready. What is left to do is create
the strategies that the ``CombinatorialSpecificationSearcher`` will use
for performing combinatorial exploration. This is given in the form of a
``StrategyPack`` which can be imported from ``comb_spec_searcher`` that
we will populate in the remainder of this example.

.. code:: python

   >>> from comb_spec_searcher import AtomStrategy, StrategyPack
   >>> pack = StrategyPack(initial_strats=[],
   ...                     inferral_strats=[],
   ...                     expansion_strats=[],
   ...                     ver_strats=[AtomStrategy()],
   ...                     name=("Finding specification for words avoiding "
   ...                           "consecutive patterns."))

Strategies are functions that take as input a class ``C`` and produce
rules about ``C``. The types of strategies are as follows: -
``initial_strats``: yields rules for classes - ``inferral_strats``:
returns a single equivalence rule - ``expansion_strats``: yields rules
for classes - ``ver_strats``: returns a rule when the count of a class
is known.

In our pack we have already added the AtomStrategy. This will verify any
combinatorial class that is an atom, in particular this is determined by the
``is_atom`` method we implemented on ``CombinatorialClass``. To get the
enumeration at the end, the strategy also uses the method
``minimum_size_of_object`` on ``CombinatorialClass``. As we've implemented
these two methods already, we are free to use the ``AtomStrategy``.

Now we will create our first strategy. Every word over the alphabet ``Σ``
starting with prefix ``p`` is either just ``p`` or has prefix ``pa`` for some
``a`` in ``Σ``. This rule is splitting the original into disjoint subsets. We
call a rule using disjoint union a ``DisjointUnionStrategy``. Although in this
case thereis a unique rule created by the strategy, strategies are assumed to
create multiple rules, and as such should be implemented as generators.

.. code:: python

   >>> from comb_spec_searcher import DisjointUnionStrategy


   >>> class ExpansionStrategy(DisjointUnionStrategy):
   ...     def decomposition_function(self, avoiding_with_prefix):
   ...        if not avoiding_with_prefix.just_prefix:
   ...           alphabet, prefix, patterns = (
   ...                 avoiding_with_prefix.alphabet,
   ...                 avoiding_with_prefix.prefix,
   ...                 avoiding_with_prefix.patterns,
   ...           )
   ...           children = [AvoidingWithPrefix(prefix, patterns, alphabet, True)]
   ...           for a in alphabet:
   ...                 ends_with_a = AvoidingWithPrefix(prefix + a, patterns, alphabet)
   ...                 children.append(ends_with_a)
   ...           return tuple(children)
   ...
   ...     def formal_step(self):
   ...        return "Either just the prefix, or append a letter from the alphabet"
   ...
   ...     def forward_map(self, avoiding_with_prefix, word, children=None):
   ...        """
   ...        The backward direction of the underlying bijection used for object
   ...        generation and sampling.
   ...        """
   ...        assert isinstance(word, Word)
   ...        if children is None:
   ...           children = self.decomposition_function(avoiding_with_prefix)
   ...           assert children is not None
   ...        if len(word) == len(avoiding_with_prefix.prefix):
   ...           return (word,) + tuple(None for i in range(len(children) - 1))
   ...        for idx, child in enumerate(children[1:]):
   ...           if word[: len(child.prefix)] == child.prefix:
   ...                 return (
   ...                    tuple(None for _ in range(idx + 1))
   ...                    + (word,)
   ...                    + tuple(None for _ in range(len(children) - idx - 1))
   ...                 )
   ...
   ...     def __str__(self):
   ...        return self.formal_step()
   ...
   ...     def __repr__(self):
   ...        return self.__class__.__name__ + "()"
   ...
   ...     @classmethod
   ...     def from_dict(cls, d):
   ...        return cls()


The final strategy we will need is one that peels off much as possible
from the front of the prefix ``p`` such that the avoidance conditions
are unaffected. This should then give a rule that is a cartesian product
of the part that is peeled off together with the words whose prefix is
that of the remainder of the original prefix. We call rules whose
constructor is cartesian product a ``DecompositionRule``.

.. code:: python

   >>> from comb_spec_searcher import CartesianProductStrategy


   >>> class RemoveFrontOfPrefix(CartesianProductStrategy):
   ...     def decomposition_function(self, avoiding_with_prefix):
   ...        """If the k is the maximum size of a pattern to be avoided, then any
   ...        occurrence using indices further to the right of the prefix can use at
   ...        most the last k - 1 letters in the prefix."""
   ...        if not avoiding_with_prefix.just_prefix:
   ...           safe = self.index_safe_to_remove_up_to(avoiding_with_prefix)
   ...           if safe > 0:
   ...                 prefix, patterns, alphabet = (
   ...                    avoiding_with_prefix.prefix,
   ...                    avoiding_with_prefix.patterns,
   ...                    avoiding_with_prefix.alphabet,
   ...                 )
   ...                 start_prefix = prefix[:safe]
   ...                 end_prefix = prefix[safe:]
   ...                 start = AvoidingWithPrefix(start_prefix, patterns, alphabet, True)
   ...                 end = AvoidingWithPrefix(end_prefix, patterns, alphabet)
   ...                 return (start, end)
   ...
   ...     def index_safe_to_remove_up_to(self, avoiding_with_prefix):
   ...        prefix, patterns = (
   ...           avoiding_with_prefix.prefix,
   ...           avoiding_with_prefix.patterns,
   ...        )
   ...        # safe will be the index of the prefix in which we can remove upto without
   ...        # affecting the avoidance conditions
   ...        m = max(len(p) for p in patterns) if patterns else 1
   ...        safe = max(0, len(prefix) - m + 1)
   ...        for i in range(safe, len(prefix)):
   ...           end = prefix[i:]
   ...           if any(end == patt[: len(end)] for patt in patterns):
   ...                 break
   ...           safe = i + 1
   ...        return safe
   ...
   ...     def formal_step(self):
   ...        return "removing redundant prefix"
   ...
   ...     def backward_map(self, avoiding_with_prefix, words, children=None):
   ...        """
   ...        The forward direction of the underlying bijection used for object
   ...        generation and sampling.
   ...        """
   ...        assert len(words) == 2
   ...        assert isinstance(words[0], Word)
   ...        assert isinstance(words[1], Word)
   ...        if children is None:
   ...           children = self.decomposition_function(avoiding_with_prefix)
   ...           assert children is not None
   ...        return Word(words[0] + words[1])
   ...
   ...     def forward_map(self, comb_class, word, children=None):
   ...        """
   ...        The backward direction of the underlying bijection used for object
   ...        generation and sampling.
   ...        """
   ...        assert isinstance(word, Word)
   ...        if children is None:
   ...           children = self.decomposition_function(comb_class)
   ...           assert children is not None
   ...        return Word(children[0].prefix), Word(word[len(children[0].prefix) :])
   ...
   ...     @classmethod
   ...     def from_dict(cls, d):
   ...        return cls()
   ...
   ...     def __str__(self):
   ...        return self.formal_step()
   ...
   ...     def __repr__(self):
   ...        return self.__class__.__name__ + "()"

With these three strategies we are now ready to perform combinatorial
exploration using the following pack.

.. code:: python

   >>> pack = StrategyPack(initial_strats=[RemoveFrontOfPrefix()],
   ...                     inferral_strats=[],
   ...                     expansion_strats=[[ExpansionStrategy()]],
   ...                     ver_strats=[AtomStrategy()],
   ...                     name=("Finding specification for words avoiding "
   ...                           "consecutive patterns."))

First we need to create the combinatorial class we want to count. For
example, consider the words over the alphabet ``{a, b}`` that avoid
``ababa`` and ``babb``. This class can be created using our initialise
function.

.. code:: python

   >>> prefix = ''
   >>> patterns = ['ababa', 'babb']
   >>> alphabet = ['a', 'b']
   >>> start_class = AvoidingWithPrefix(prefix, patterns, alphabet)

We can then initialise our ``CombinatorialSpecificationSearcher``, and
use the ``auto_search`` function which will return a
``CombinatorialSpecification`` assuming one is found (which in this case always
will).

.. code:: python

   >>> from comb_spec_searcher import CombinatorialSpecificationSearcher


   >>> searcher = CombinatorialSpecificationSearcher(start_class, pack)
   >>> spec = searcher.auto_search()
   >>> # spec.show() will display the specification in your browser

Now that we have a ``CombinatorialSpecification``, the obvious
thing we want to do is find the generating function for the class that
counts the number of objects of each size. This can be done by using the
``get_genf`` methods on ``CombinatorialSpecification``.

Finally, in order to get initial terms, you will also need to implement
the ``objects_of_size`` function which should yield all of the objects
of a given size in the class.

.. code:: python

   >>> from itertools import product

   >>> def objects_of_size(self, size):
   ...     """Yield the words of given size that start with prefix and avoid the
   ...     patterns. If just_prefix, then only yield that word."""
   ...     def possible_words():
   ...         """Yield all words of given size over the alphabet with prefix"""
   ...         if len(self.prefix) > size:
   ...            return
   ...         for letters in product(self.alphabet,
   ...                                 repeat=size - len(self.prefix)):
   ...             yield self.prefix + "".join(a for a in letters)
   ...
   ...     if self.just_prefix:
   ...         if size == len(self.prefix) and not self.is_empty():
   ...             yield self.prefix
   ...         return
   ...     for word in possible_words():
   ...         if all(patt not in word for patt in self.patterns):
   ...             yield word
   >>> AvoidingWithPrefix.objects_of_size = objects_of_size

With these in place if we then call the ``get_genf`` function

.. code:: python

   >>> spec.get_genf()
   -(x + 1)*(x**2 - x + 1)**2*(x**2 + x + 1)/(x**6 + x**3 - x**2 + 2*x - 1)

we see that the the generating function is
``F = -(x**7 + x**5 + x**4 + x**3 + x**2 + 1)/(x**6 + x**3 - x**2 + 2*x - 1)``.

Moreover, we can get directly the number of objects by size with the method
`count_objects_of_size`.

.. code:: python

   >>> [spec.count_objects_of_size(i) for i in range(11)]
   [1, 2, 4, 8, 15, 27, 48, 87, 157, 283, 511]

You can now try this yourself using the file ``example.py``, which can
count any set of words avoiding consecutive patterns.

Now we will demonstrate how a bijection can be found between classes.
We will first need a couple of imports.

.. code:: python

   >>> from comb_spec_searcher import find_bijection_between, Bijection

We start by defining our two classes that we wish to find a bijection between.

.. code:: python

   >>> prefix1 = ''
   >>> patterns1 = ["00"]
   >>> alphabet1 = ['0', '1']
   >>> class1 = AvoidingWithPrefix(prefix1, patterns1, alphabet1)
   >>> prefix2 = ''
   >>> patterns2 = ["bb"]
   >>> alphabet2 = ['a', 'b']
   >>> class2 = AvoidingWithPrefix(prefix2, patterns2, alphabet2)

To find a bijection we expand the universe given a pack for both classes
and try to construct specifications that are parallel. If the atoms can not
be compared with ``==`` we will need to supply our own equals function.

.. code:: python

   >>> def atom_cmp(class1, class2):
   ...     return len(class1.prefix) == len(class2.prefix)
   >>> searcher1 = CombinatorialSpecificationSearcher(class1, pack)
   >>> searcher2 = CombinatorialSpecificationSearcher(class2, pack)

We get two parallel specs if successful, ``None`` otherwise.

.. code:: python

   >>> specs = find_bijection_between(searcher1, searcher2, atom_cmp)
   >>> spec1, spec2 = specs
   >>> bijection = Bijection.construct(spec1, spec2, atom_cmp)

We can use the `Bijection` object to map (either way) sampled objects
from the sepcifications.

... code:: python

   >>> for i in range(10):
   ...     for w in spec1.generate_objects_of_size(i):
   ...         assert w == bijection.inverse_map(bijection.map(w))
   ...     for w in spec2.generate_objects_of_size(i):
   ...         assert w == bijection.map(bijection.inverse_map(w))
   ...
   >>>

Whether we find a bijection or not (when one exists) is highly 
dependent on the packs chosen.