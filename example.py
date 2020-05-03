"""
In this file an example of how to perform combinatorial exploration on words
with respect to factor order is given.

>>> alphabet = ['a', 'b']
>>> start_class = AvoidingWithPrefix('', ['b'], alphabet)
>>> searcher = CombinatorialSpecificationSearcher(start_class, pack)
>>> specification = searcher.auto_search(status_update=10)
>>> [specification.count_objects_of_size(n=i) for i in range(10)]
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

>>> start_class = AvoidingWithPrefix('', ['ab'], alphabet)
>>> searcher = CombinatorialSpecificationSearcher(start_class, pack)
>>> specification = searcher.auto_search(status_update=10)
>>> [specification.count_objects_of_size(n=i) for i in range(10)]
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

>>> start_class = AvoidingWithPrefix('', ['aa', 'bb'], alphabet)
>>> searcher = CombinatorialSpecificationSearcher(start_class, pack)
>>> specification = searcher.auto_search(status_update=10)
>>> [specification.count_objects_of_size(n=i) for i in range(10)]
[1, 2, 2, 2, 2, 2, 2, 2, 2, 2]

>>> start_class = AvoidingWithPrefix('', ['bb'], alphabet)
>>> searcher = CombinatorialSpecificationSearcher(start_class, pack)
>>> specification = searcher.auto_search(status_update=10)
>>> [specification.count_objects_of_size(n=i) for i in range(11)]
[1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]

>>> start_class = AvoidingWithPrefix('', ['ababa', 'babb'], alphabet)
>>> searcher = CombinatorialSpecificationSearcher(start_class, pack)
>>> specification = searcher.auto_search()
>>> [specification.count_objects_of_size(n=i) for i in range(11)]
[1, 2, 4, 8, 15, 27, 48, 87, 157, 283, 511]
>>> specification.count_objects_of_size(n=15)
9798
"""
from typing import Iterable, Iterator, Optional, Tuple, Union

from sympy import var

from comb_spec_searcher import (
    CartesianProductStrategy,
    CombinatorialClass,
    CombinatorialObject,
    CombinatorialSpecificationSearcher,
    DisjointUnionStrategy,
    StrategyPack,
    VerificationStrategy,
)


class Word(str, CombinatorialObject):
    pass


class AvoidingWithPrefix(CombinatorialClass[Word]):
    """The set of words over the 'alphabet' starting with 'prefix' that avoid
    the consecutive 'patterns'."""

    def __init__(
        self,
        prefix: str,
        patterns: Iterable[str],
        alphabet: Iterable[str],
        just_prefix: bool = False,
    ):
        if not all(isinstance(l, str) and len(l) == 1 for l in alphabet):
            raise ValueError("Alphabet must be an iterable of letters.")
        self.alphabet = tuple(sorted(alphabet))
        if not self.word_over_alphabet(prefix):
            raise ValueError("Prefix must be a word over the given alphabet.")
        self.prefix: Word = Word(prefix)
        if not all(self.word_over_alphabet(patt) for patt in patterns):
            raise ValueError("Patterns must be words over the given alphabet.")
        self.patterns: Tuple[Word, ...] = tuple(sorted(map(Word, patterns)))
        self.just_prefix = just_prefix
        super().__init__()

    def word_over_alphabet(self, word: str) -> bool:
        """Return True if word consists of letters from the alphabet."""
        return isinstance(word, str) and all(l in self.alphabet for l in word)

    # methods required for combinatorial exploration

    def is_empty(self) -> bool:
        """Return True if no word over the alphabet avoiding the patterns has
        this prefix."""
        return bool(any(p in self.prefix for p in self.patterns))

    def to_jsonable(self) -> dict:
        """Return a jsonable object of the combinatorial class."""
        return {
            "prefix": self.prefix,
            "patterns": tuple(sorted(self.patterns)),
            "alphabet": tuple(sorted(self.alphabet)),
            "just_prefix": int(self.just_prefix),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "AvoidingWithPrefix":
        """Create an instance of the class from the dictionary returned by the
        'to_jsonable' method."""
        return cls(
            d["prefix"], d["patterns"], d["alphabet"], bool(int(d["just_prefix"])),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AvoidingWithPrefix):
            return NotImplemented
        return bool(
            self.alphabet == other.alphabet
            and self.prefix == other.prefix
            and self.patterns == other.patterns
            and self.just_prefix == other.just_prefix
        )

    def __hash__(self) -> int:
        return hash(
            hash(self.prefix)
            + hash(self.patterns)
            + hash(self.alphabet)
            + hash(self.just_prefix)
        )

    def __str__(self) -> str:
        if self.just_prefix:
            return "The word {}".format(self.prefix)
        return "Words over {{{}}} avoiding {{{}}} with prefix {}" "".format(
            ", ".join(l for l in self.alphabet),
            ", ".join(p for p in self.patterns),
            self.prefix if self.prefix else '""',
        )

    def __repr__(self) -> str:
        return "AvoidindWithPrefix({}, {}, {}".format(
            repr(self.prefix), repr(self.patterns), repr(self.alphabet)
        )

    # Method required to get the counts

    def is_epsilon(self) -> bool:
        return self.prefix == "" and self.just_prefix

    def is_atom(self) -> bool:
        return len(self.prefix) == 1 and self.just_prefix

    def is_positive(self) -> bool:
        return len(self.prefix) > 0


# the strategies


class ExpansionStrategy(DisjointUnionStrategy[AvoidingWithPrefix]):
    def decomposition_function(
        self, avoiding_with_prefix: AvoidingWithPrefix
    ) -> Optional[Tuple[AvoidingWithPrefix, ...]]:
        if not avoiding_with_prefix.just_prefix:
            alphabet, prefix, patterns = (
                avoiding_with_prefix.alphabet,
                avoiding_with_prefix.prefix,
                avoiding_with_prefix.patterns,
            )
            children = [AvoidingWithPrefix(prefix, patterns, alphabet, True)]
            for a in alphabet:
                ends_with_a = AvoidingWithPrefix(prefix + a, patterns, alphabet)
                children.append(ends_with_a)
            return tuple(children)

    def formal_step(self) -> str:
        return "Either just the prefix, or append a letter from the alphabet"

    def forward_map(
        self,
        avoiding_with_prefix: AvoidingWithPrefix,
        word: CombinatorialObject,
        children: Optional[Tuple[AvoidingWithPrefix, ...]] = None,
    ) -> Tuple[Word, ...]:
        """
        The backward direction of the underlying bijection used for object
        generation and sampling.
        """
        assert isinstance(word, Word)
        if children is None:
            children = self.decomposition_function(avoiding_with_prefix)
            assert children is not None
        if len(word) == len(avoiding_with_prefix.prefix):
            return (word,) + tuple(None for i in range(len(children) - 1))
        for idx, child in enumerate(children[1:]):
            if word[: len(child.prefix)] == child.prefix:
                return (
                    tuple(None for _ in range(idx + 1))
                    + (child,)
                    + tuple(None for _ in range(len(children) - idx - 1))
                )

    def __str__(self) -> str:
        return self.formal_step()

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    @classmethod
    def from_dict(cls, d) -> "ExpansionStrategy":
        return cls()


class OnlyPrefix(VerificationStrategy[AvoidingWithPrefix]):
    def formal_step(self) -> str:
        return "its just a word"

    def verified(self, avoiding_with_prefix: AvoidingWithPrefix) -> bool:
        """
        Returns True if enumeration strategy works for the combinatorial class.
        """
        return avoiding_with_prefix.just_prefix

    def count_objects_of_size(
        self, comb_class: AvoidingWithPrefix, **parameters: int
    ) -> int:
        """Verification strategies must contain a method to count the objects."""
        if self.verified(comb_class) and parameters["n"] == len(comb_class.prefix):
            return 1
        return 0

    def generate_objects_of_size(
        self, comb_class: AvoidingWithPrefix, **parameters: int
    ) -> Iterator[Word]:
        """Verification strategies must contain a method to generate the objects."""
        if self.verified(comb_class) and parameters["n"] == len(comb_class.prefix):
            yield Word(comb_class.prefix)

    def get_genf(self, comb_class: AvoidingWithPrefix):
        x = var("x")
        return x ** len(comb_class.prefix)

    @classmethod
    def from_dict(cls, d) -> "OnlyPrefix":
        return cls()

    def __str__(self) -> str:
        return self.formal_step()

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"


class RemoveFrontOfPrefix(CartesianProductStrategy[AvoidingWithPrefix]):
    def decomposition_function(
        self, avoiding_with_prefix: AvoidingWithPrefix
    ) -> Union[Tuple[AvoidingWithPrefix, ...], None]:
        """If the k is the maximum length of a pattern to be avoided, then any
        occurrence using indices further to the right of the prefix can use at
        most the last k - 1 letters in the prefix."""
        if not avoiding_with_prefix.just_prefix:
            safe = self.index_safe_to_remove_up_to(avoiding_with_prefix)
            if safe > 0:
                prefix, patterns, alphabet = (
                    avoiding_with_prefix.prefix,
                    avoiding_with_prefix.patterns,
                    avoiding_with_prefix.alphabet,
                )
                start_prefix = prefix[:safe]
                end_prefix = prefix[safe:]
                start = AvoidingWithPrefix(start_prefix, patterns, alphabet, True)
                end = AvoidingWithPrefix(end_prefix, patterns, alphabet)
                return (start, end)

    def index_safe_to_remove_up_to(self, avoiding_with_prefix: AvoidingWithPrefix):
        prefix, patterns = (
            avoiding_with_prefix.prefix,
            avoiding_with_prefix.patterns,
        )
        # safe will be the index of the prefix in which we can remove upto without
        # affecting the avoidance conditions
        safe = max(0, len(prefix) - max(len(p) for p in patterns) + 1)
        for i in range(safe, len(prefix)):
            end = prefix[i:]
            if any(end == patt[: len(end)] for patt in patterns):
                break
            safe = i + 1
        return safe

    def formal_step(self) -> str:
        return "removing redundant prefix"

    def backward_map(
        self,
        avoiding_with_prefix: AvoidingWithPrefix,
        words: Tuple[CombinatorialObject, ...],
        children: Optional[Tuple[AvoidingWithPrefix, ...]] = None,
    ) -> Word:
        """
        The forward direction of the underlying bijection used for object
        generation and sampling.
        """
        assert len(words) == 2
        assert isinstance(words[0], Word)
        assert isinstance(words[1], Word)
        if children is None:
            children = self.decomposition_function(avoiding_with_prefix)
            assert children is not None
        return Word(words[0] + words[1])

    def forward_map(
        self,
        comb_class: AvoidingWithPrefix,
        word: CombinatorialObject,
        children: Optional[Tuple[AvoidingWithPrefix, ...]] = None,
    ) -> Tuple[Word, ...]:
        """
        The backward direction of the underlying bijection used for object
        generation and sampling.
        """
        assert isinstance(word, Word)
        if children is None:
            children = self.decomposition_function(comb_class)
            assert children is not None
        return Word(children[0].prefix), Word(word[len(children[0].prefix) :])

    @classmethod
    def from_dict(cls, d):
        return cls()

    def __str__(self) -> str:
        return self.formal_step()

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"


pack = StrategyPack(
    initial_strats=[RemoveFrontOfPrefix()],
    inferral_strats=[],
    expansion_strats=[[ExpansionStrategy()]],
    ver_strats=[OnlyPrefix()],
    name=("Finding specification for words avoiding consecutive patterns."),
)


if __name__ == "__main__":
    example_alphabet = input(
        ("Input the alphabet (letters should be separated by a" " comma):")
    ).split(",")
    example_patterns = tuple(
        map(
            Word,
            input(
                (
                    "Input the patterns to be avoided (patterns should be "
                    "separated by a comma):"
                )
            ).split(","),
        )
    )

    start_class = AvoidingWithPrefix(Word(), example_patterns, example_alphabet)
    searcher = CombinatorialSpecificationSearcher(start_class, pack, debug=True)
    spec = searcher.auto_search(status_update=10)
    print(spec)
    print(spec.get_genf())
    import time

    for n in range(20):
        print("=" * 10, n, "=" * 10)
        start_time = time.time()
        print(spec.count_objects_of_size(n=n))
        print("Counting time:", round(time.time() - start_time, 2), "seconds")
        start_time = time.time()
        c = 0
        for _ in spec.generate_objects_of_size(n=n):
            c += 1
        print(c)
        print("Object generation time:", round(time.time() - start_time, 2), "seconds")
