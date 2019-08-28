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
thesis <https://skemman.is/handle/1946/31663>`__ for more details.

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
   ...         if self.just_prefix:
   ...             return "The word {}".format(self.prefix)
   ...         return ("Words over {{{}}} avoiding {{{}}} with prefix {}"
   ...                 "".format(", ".join(l for l in self.alphabet),
   ...                           ", ".join(p for p in self.patterns),
   ...                           self.prefix if self.prefix else '""'))
   ...
   ...     def __repr__(self):
   ...         return "AvoidingWithPrefix({}, {}, {}".format(repr(self.prefix),
   ...                                                       repr(self.patterns),
   ...                                                       repr(self.alphabet))

Perhaps the most important function to be implemented is the
``is_empty`` function. This should return ``True`` if there are no
objects of any length in the class, otherwise ``False``. If it is not
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

   ...     def is_epsilon(self):
   ...         """ Returns True if the generating function is 1"""
   ...         return self.prefix == "" and self.just_prefix
   ...
   ...     def is_atom(self):
   ...         """ Returns True if the generating function is x"""
   ...         return len(self.prefix) == 1 and self.just_prefix
   ...
   ...     def is_positive(self):
   ...         """ Returns True if the constant term of the generating function is 0"""
   ...         return len(self.prefix) > 0

Our ``CombinatorialClass`` is now ready. What is left to do is create
the strategies that the ``CombinatorialSpecificationSearcher`` will use
for performing combinatorial exploration. This is given in the form of a
``StrategyPack`` which can be imported from ``comb_spec_searcher`` that
we will populate in the remainder of this example.

.. code:: python

   >>> from comb_spec_searcher import StrategyPack
   >>> pack = StrategyPack(initial_strats=[],
   ...                     inferral_strats=[],
   ...                     expansion_strats=[],
   ...                     ver_strats=[],
   ...                     name=("Finding specification for words avoiding "
   ...                           "consecutive patterns."))

Strategies are functions that take as input a class ``C`` and produce
rules about ``C``. The types of strategies are as follows: -
``initial_strats``: yields rules for classes - ``inferral_strats``:
returns a single equivalence rule - ``expansion_strats``: yields rules
for classes - ``ver_strats``: returns a rule when the count of a class
is known

For example, every word over the alphabet ``Σ`` starting with prefix
``p`` is either just ``p`` or has prefix ``pa`` for some ``a`` in ``Σ``.
This rule is splitting the original into disjoint subsets. We call a
rule using disjoint union a ``BatchRule``. Although in this case there
is a unique rule created by the strategy, strategies are assumed to
create multiple rules, and as such should be implemented as generators.

.. code:: python

   >>> from comb_spec_searcher import BatchRule


   >>> def expansion(avoiding_with_prefix, **kwargs):
   ...     if avoiding_with_prefix.just_prefix:
   ...         return
   ...     alphabet, prefix, patterns = (avoiding_with_prefix.alphabet,
   ...                                   avoiding_with_prefix.prefix,
   ...                                   avoiding_with_prefix.patterns)
   ...     # either just p
   ...     comb_classes = [AvoidingWithPrefix(prefix, patterns, alphabet, True)]
   ...     for a in alphabet:
   ...         # or has prefix pa for some a in Σ.
   ...         ends_with_a = AvoidingWithPrefix(prefix + a, patterns, alphabet)
   ...         comb_classes.append(ends_with_a)
   ...     yield BatchRule(("The next letter in the prefix is one of {{{}}}"
   ...                      "".format(", ".join(l for l in alphabet))),
   ...                     comb_classes)

The classes that we will verify are those that consist of just the
prefix. To verify these we create a new strategy that returns a
``VerificationRule`` when this is the case.

.. code:: python

   >>> from comb_spec_searcher import VerificationRule


   >>> def only_prefix(avoiding_with_prefix, **kwargs):
   ...     if avoiding_with_prefix.just_prefix:
   ...         return VerificationRule(("The set contains only the word {}"
   ...                                  "".format(avoiding_with_prefix.prefix)))

The final strategy we will need is one that peels off much as possible
from the front of the prefix ``p`` such that the avoidance conditions
are unaffected. This should then give a rule that is a cartesian product
of the part that is peeled off together with the words whose prefix is
that of the remainder of the original prefix. We call rules whose
constructor is cartesian product a ``DecompositionRule``.

.. code:: python

   >>> from comb_spec_searcher import DecompositionRule


   >>> def remove_front_of_prefix(avoiding_with_prefix, **kwargs):
   ...     """If the k is the maximum length of a pattern to be avoided, then any
   ...     occurrence using indices further to the right of the prefix can use at
   ...     most the last k - 1 letters in the prefix."""
   ...     if avoiding_with_prefix.just_prefix:
   ...         return
   ...     prefix, patterns, alphabet = (avoiding_with_prefix.prefix,
   ...                                   avoiding_with_prefix.patterns,
   ...                                   avoiding_with_prefix.alphabet)
   ...     # safe will be the index of the prefix in which we can remove upto without
   ...     # affecting the avoidance conditions
   ...     safe = max(0, len(prefix) - max(len(p) for p in patterns) + 1)
   ...     for i in range(safe, len(prefix)):
   ...         end = prefix[i:]
   ...         if any(end == patt[:len(end)] for patt in patterns):
   ...             break
   ...         safe = i + 1
   ...     if safe > 0:
   ...         start_prefix = prefix[:safe]
   ...         end_prefix = prefix[safe:]
   ...         start = AvoidingWithPrefix(start_prefix, patterns, alphabet, True)
   ...         end = AvoidingWithPrefix(end_prefix, patterns, alphabet)
   ...         yield DecompositionRule("Remove up to index {} of prefix".format(safe),
   ...                                 [start, end])

With these three strategies we are now ready to perform combinatorial
exploration using the following pack.

.. code:: python

   >>> pack = StrategyPack(initial_strats=[remove_front_of_prefix],
   ...                     inferral_strats=[],
   ...                     expansion_strats=[[expansion]],
   ...                     ver_strats=[only_prefix],
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
use the ``auto_search`` function which will return a ``ProofTree``
object that represents a specification assuming one is found (which in
this case always will).

.. code:: python

   >>> from comb_spec_searcher import CombinatorialSpecificationSearcher


   >>> searcher = CombinatorialSpecificationSearcher(start_class, pack)
   >>> tree = searcher.auto_search()

Now that we have a ``ProofTree`` i.e., a specification, the obvious
thing we want to do is find the generating function for the class that
counts the number of objects of each size. This can be done by using the
``get_genf`` or ``get_min_poly`` methods on ``ProofTree``. To use these
methods we will need to go back and implement a few functions in our
``CombinatorialClass``.

When you verify a class, this tells the ``ProofTree`` class that it can
get the generating function by calling the ``get_genf`` (and/or the
``get_min_poly``) function on ``CombinatorialClass``. In our case, we
verified exactly when the class was only the prefix, say ``p``. The
generating function of this is clearly ``x**len(p)``. We add these
methods to our class.

.. code:: python

   >>> from sympy import abc, var

   >>> def get_genf(self, **kwargs):
   ...     """Return the generating function when only a prefix."""
   ...     if self.just_prefix:
   ...         if self.is_empty():
   ...             return 0
   ...         else:
   ...             return abc.x**len(self.prefix)
   >>> AvoidingWithPrefix.get_genf = get_genf
   >>> def get_min_poly(self, *args, **kwargs):
   ...     """Return the minimum polynomial satisfied by the generating function
   ...     of the combinatorial class (in terms of F)."""
   ...     if self.just_prefix:
   ...         if self.is_empty():
   ...             return 0
   ...         else:
   ...             return var('F') - abc.x**len(self.prefix)
   >>> AvoidingWithPrefix.get_min_poly = get_min_poly

Finally, in order to get initial terms, you will also need to implement
the ``objects_of_length`` function which should yield all of the objects
of a given length in the class.

.. code:: python

   >>> from itertools import product

   >>> def objects_of_length(self, length):
   ...     """Yield the words of given length that start with prefix and avoid the
   ...     patterns. If just_prefix, then only yield that word."""
   ...     def possible_words():
   ...         """Yield all words of given length over the alphabet with prefix"""
   ...         for letters in product(self.alphabet,
   ...                                 repeat=length - len(self.prefix)):
   ...             yield self.prefix + "".join(a for a in letters)
   ...
   ...     if self.just_prefix:
   ...         if length == len(self.prefix) and not self.is_empty():
   ...             yield self.prefix
   ...         return
   ...     for word in possible_words():
   ...         if all(patt not in word for patt in self.patterns):
   ...             yield word
   >>> AvoidingWithPrefix.objects_of_length = objects_of_length

With these in place if we then call the ``get_min_poly`` function with
the flag ``solve=True``

.. code:: python

   >>> tree.get_min_poly()
   F*x**6 + F*x**3 - F*x**2 + 2*F*x - F + x**7 + x**5 + x**4 + x**3 + x**2 + 1
   >>> tree.get_genf()
   -(x + 1)*(x**2 - x + 1)**2*(x**2 + x + 1)/(x**6 + x**3 - x**2 + 2*x - 1)

we see that the minimum polynomial satisfied by the generating function
``F`` is
``F*(x**6 + x**3 - x**2 + 2*x - 1) + x**7 + x**5 + x**4 + x**3 + x**2 + 1``
and moreover
``F = -(x**7 + x**5 + x**4 + x**3 + x**2 + 1)/(x**6 + x**3 - x**2 + 2*x - 1)``.

Moreover, we can get directly the number of objects by length with the method
`count_objects_of_length`.

.. code:: python

   >>> [tree.count_objects_of_length(i) for i in range(11)]
   [1, 2, 4, 8, 15, 27, 48, 87, 157, 283, 511]

You can now try this yourself using the file ``example.py``, which can
count any set of words avoiding consecutive patterns.
