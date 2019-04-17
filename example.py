"""
In this file an example of how to perform combinatorial exploration on words
with respect to factor order is given.
"""
from itertools import product
from comb_spec_searcher import (BatchRule, CombinatorialClass,
                                CombinatorialSpecificationSearcher,
                                DecompositionRule, StrategyPack,
                                VerificationRule)
from sympy import abc, var


class AvoidingWithPrefix(CombinatorialClass):
    def __init__(self, prefix, patterns, alphabet, just_prefix=False):
        if not all(isinstance(l, str) and len(l) == 1 for l in alphabet):
            raise ValueError("Alphabet must be an iterable of letters.")
        self.alphabet = frozenset(alphabet)
        if not self.word_over_alphabet(prefix):
            raise ValueError("Prefix must be a word over the given alphabet.")
        self.prefix = prefix
        if not all(self.word_over_alphabet(patt) for patt in patterns):
            raise ValueError("Patterns must be words over the given alphabet.")
        self.patterns = frozenset(patterns)
        self.just_prefix = just_prefix

    def word_over_alphabet(self, word):
        """Return True if word consists of letters from the alphabet."""
        return isinstance(word, str) and all(l in self.alphabet for l in word)

    # methods required by for combinatorial exploration

    def is_empty(self):
        """Return True if no word over the alphabet avoiding the patterns has
        this prefix."""
        return any(p in self.prefix for p in self.patterns)

    def to_jsonable(self):
        """Return a jsonable object of the combinatorial class."""
        return {"prefix": self.prefix,
                "patterns": tuple(sorted(self.patterns)),
                "alphabet": tuple(sorted(self.alphabet)),
                "just_prefix": int(self.just_prefix)}

    # not required, but why would you no implement this when you implement
    # 'to_jsonable'?
    @classmethod
    def from_dict(cls, data):
        """Create an instance of the class from the dictionary returned by the
        'to_jsonable' method."""
        return AvoidingWithPrefix(data['prefix'],
                                  data['patterns'],
                                  data['alphabet'],
                                  bool(int(data['just_prefix'])))

    # methods for computing the generating function

    def get_genf(self, **kwargs):
        """Return the generating function when only a prefix."""
        if self.just_prefix:
            if self.is_empty():
                return 0
            else:
                return abc.x**len(self.prefix)
        else:
            raise NotImplementedError(("Only implemented get_genf for only "
                                       "prefix."))

    def get_min_poly(self, *args, **kwargs):
        """Return the minimum polynomial satisfied by the generating function
        of the combinatorial class (in terms of F)."""
        if self.just_prefix:
            if self.is_empty():
                return 0
            else:
                return var('F') - abc.x**len(self.prefix)
        else:
            raise NotImplementedError(("Only implemented get_min_poly for "
                                       "only prefix."))

    def objects_of_length(self, length):
        """Yield the words of given length that start with prefix and avoid the
        patterns. If just_prefix, then only yield that word."""
        def possible_words():
            """Yield all words of given length over the alphabet with prefix"""
            for letters in product(self.alphabet,
                                   repeat=length - len(self.prefix)):
                yield self.prefix + "".join(a for a in letters)

        if self.just_prefix:
            if length == len(self.prefix) and not self.is_empty():
                yield self.prefix
            return
        for word in possible_words():
            if all(patt not in word for patt in self.patterns):
                yield word

    # The dunder methods required to perform combinatorial exploration

    def __eq__(self, other):
        return (self.alphabet == other.alphabet and
                self.prefix == other.prefix and
                self.patterns == other.patterns and
                self.just_prefix == other.just_prefix)

    def __hash__(self):
        return hash(hash(self.prefix) + hash(self.patterns) +
                    hash(self.alphabet) + hash(self.just_prefix))

    def __str__(self):
        if self.just_prefix:
            return "The word {}".format(self.prefix)
        return ("Words over {{{}}} avoiding {{{}}} with prefix {}"
                "".format(", ".join(l for l in self.alphabet),
                          ", ".join(p for p in self.patterns),
                          self.prefix if self.prefix else '""'))

    def __repr__(self):
        return "AvoidindWithPrefix({}, {}, {}".format(repr(self.prefix),
                                                      repr(self.patterns),
                                                      repr(self.alphabet))


def expansion(avoiding_with_prefix, **kwargs):
    """Every word with prefix p is either just p or of the form pa for some a
    in the alphabet."""
    if avoiding_with_prefix.just_prefix:
        return
    alphabet, prefix, patterns = (avoiding_with_prefix.alphabet,
                                  avoiding_with_prefix.prefix,
                                  avoiding_with_prefix.patterns)
    comb_classes = [AvoidingWithPrefix(prefix, patterns, alphabet, True)]
    for a in alphabet:
        ends_with_a = AvoidingWithPrefix(prefix + a, patterns, alphabet)
        comb_classes.append(ends_with_a)
    yield BatchRule(("The next letter in the prefix is one of {{{}}}"
                     "".format(", ".join(l for l in alphabet))),
                    comb_classes)


def only_prefix(avoiding_with_prefix, **kwargs):
    """If it is only the prefix, then the enumeration is x**len(p)."""
    if avoiding_with_prefix.just_prefix:
        return VerificationRule(("The set contains only the word {}"
                                 "".format(avoiding_with_prefix.prefix)))


def remove_front_of_prefix(avoiding_with_prefix, **kwargs):
    """If the k is the maximum length of a pattern to be avoided, then any
    occurrence using indices further to the right of the prefix can use at
    most the last k - 1 letters in the prefix."""
    if avoiding_with_prefix.just_prefix:
        return
    prefix, patterns, alphabet = (avoiding_with_prefix.prefix,
                                  avoiding_with_prefix.patterns,
                                  avoiding_with_prefix.alphabet)
    # safe will be the index of the prefix in which we can remove upto without
    # affecting the avoidance conditions
    safe = max(0, len(prefix) - max(len(p) for p in patterns) + 1)
    if safe > 0:
        start_prefix = prefix[:safe]
        end_prefix = prefix[safe:]
        start = AvoidingWithPrefix(start_prefix, patterns, alphabet, True)
        end = AvoidingWithPrefix(end_prefix, patterns, alphabet)
        yield DecompositionRule("Remove up to index {} of prefix".format(safe),
                                [start, end])


pack = StrategyPack(initial_strats=[remove_front_of_prefix],
                    inferral_strats=[],
                    expansion_strats=[[expansion]],
                    ver_strats=[only_prefix],
                    name=("Finding specification for words avoiding "
                          "consecutive patterns."))


if __name__ == "__main__":
    alphabet = input(("Input the alphabet (letters should be separated by a"
                      " comma):")).split(",")
    patterns = input(("Input the patterns to be avoided (patterns should be "
                      "separated by a comma):")).split(",")

    start_class = AvoidingWithPrefix("", patterns, alphabet)
    searcher = CombinatorialSpecificationSearcher(start_class, pack)

    tree = searcher.auto_search(status_update=10)
    tree.get_min_poly(solve=True)
