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


RuleKey = Tuple[int, Tuple[int, ...]]

# From constructor
Parameters = Tuple[int, ...]
ParametersMap = Callable[[Parameters], Parameters]
RelianceProfile = Tuple[Dict[str, Tuple[int, ...]], ...]
Objects = DefaultDict[Parameters, List[CombinatorialObjectType]]
ObjectsCache = List[Objects]
Terms = Counter[Parameters]  # all terms for a fixed n
TermsCache = List[Terms]  # index n contains terms for n
SubObjects = Tuple[Callable[[int], Objects], ...]
SubRecs = Tuple[Callable[..., int], ...]
SubSamplers = Tuple[Callable[..., CombinatorialObjectType], ...]
SubTerms = Tuple[Callable[[int], Terms], ...]
