import enum
from typing import (
    TYPE_CHECKING,
    Callable,
    Counter,
    DefaultDict,
    Dict,
    List,
    NamedTuple,
    Set,
    Tuple,
    TypeVar,
    Union,
)

if TYPE_CHECKING:
    from comb_spec_searcher.combinatorial_class import CombinatorialClass  # noqa: F401
    from comb_spec_searcher.combinatorial_class import CombinatorialObject  # noqa: F401
    from comb_spec_searcher.strategies.strategy import AbstractStrategy, StrategyFactory

__all__ = [
    "CombinatorialObjectType",
    "CombinatorialClassType",
    "ClassKey",
    "Key",
    "CSSstrategy",
    "RulesDict",
    "WorkPacket",
    "RuleKey",
    "Parameters",
    "ParametersMap",
    "RelianceProfile",
    "RuleBucket",
    "ForestRuleKey",
    "Objects",
    "ObjectsCache",
    "Terms",
    "TermsCache",
    "SubObjects",
    "SubRecs",
    "SubSamplers",
    "SubTerms",
]

CombinatorialObjectType = TypeVar(
    "CombinatorialObjectType", bound="CombinatorialObject"
)

CombinatorialClassType = TypeVar("CombinatorialClassType", bound="CombinatorialClass")


ClassKey = Union[bytes, CombinatorialClassType]
Key = Union[CombinatorialClassType, int]

CSSstrategy = Union["AbstractStrategy", "StrategyFactory"]
RulesDict = Dict[int, Set[Tuple[int, ...]]]


class WorkPacket(NamedTuple):
    label: int
    strategies: Tuple[CSSstrategy, ...]
    inferral: bool


@enum.unique
class RuleBucket(enum.Enum):
    UNDEFINED = enum.auto()
    VERIFICATION = enum.auto()
    EQUIV = enum.auto()
    NORMAL = enum.auto()
    REVERSE = enum.auto()


RuleKey = Tuple[int, Tuple[int, ...]]


class ForestRuleKey(NamedTuple):
    parent: int
    children: Tuple[int, ...]
    shifts: Tuple[int, ...]
    bucket: RuleBucket

    @property
    def key(self) -> RuleKey:
        return (self.parent, self.children)


# From constructor
Parameters = Tuple[int, ...]
ParametersMap = Callable[[Parameters], Parameters]
RelianceProfile = Tuple[Dict[str, Tuple[int, ...]], ...]
Objects = DefaultDict[Parameters, List[CombinatorialObjectType]]
ObjectsCache = List[Objects]
Terms = Counter[Parameters]  # all terms for a fixed n
# TermsCache = List[Terms]  # index n contains terms for n
SubObjects = Tuple[Callable[[int], Objects], ...]
SubRecs = Tuple[Callable[..., int], ...]
SubSamplers = Tuple[Callable[..., CombinatorialObjectType], ...]
SubTerms = Tuple[Callable[[int], Terms], ...]


class TermsCache:
    ALL_CACHES: List["TermsCache"] = []
    KEY_CACHE: Dict[Parameters, Parameters] = {}

    def __init__(self) -> None:
        self.data: List[Terms] = []
        self.ALL_CACHES.append(self)

    def __len__(self) -> int:
        return len(self.data)

    def append(self, terms: Terms) -> None:
        self.data.append(self.clean_keys(terms))

    def __getitem__(self, index: int) -> Terms:
        return self.data.__getitem__(index)

    @classmethod
    def clean_keys(cls, terms: Terms) -> Terms:
        return terms
        new_terms: Counter[Parameters] = Counter()
        for k, v in terms.items():
            if k not in cls.KEY_CACHE:
                cls.KEY_CACHE[k] = k
            new_terms[cls.KEY_CACHE[k]] = v
        return new_terms

    @classmethod
    def num_keys(cls):
        tot = 0
        for cache in cls.ALL_CACHES:
            for terms in cache:
                for key in terms:
                    tot += 1
        return tot

    @classmethod
    def num_key_ids(cls):
        ids = set()
        for cache in cls.ALL_CACHES:
            for terms in cache:
                for key in terms:
                    ids.add(id(key))
        return len(ids)

    @classmethod
    def num_unique_keys(cls):
        keys = set()
        for cache in cls.ALL_CACHES:
            for terms in cache:
                for key in terms:
                    keys.add(key)
        return len(keys)
