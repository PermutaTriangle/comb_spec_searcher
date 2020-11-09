from typing import (
    TYPE_CHECKING,
    Callable,
    Counter,
    DefaultDict,
    Dict,
    List,
    NamedTuple,
    NewType,
    Set,
    Tuple,
    TypeVar,
    Union,
)

if TYPE_CHECKING:
    from comb_spec_searcher.combinatorial_class import CombinatorialClass  # noqa: F401
    from comb_spec_searcher.combinatorial_class import CombinatorialObject  # noqa: F401
    from comb_spec_searcher.strategies.strategy import AbstractStrategy, StrategyFactory

Label = NewType("Label", int)

CombinatorialObjectType = TypeVar(
    "CombinatorialObjectType", bound="CombinatorialObject"
)
CombinatorialClassType = TypeVar("CombinatorialClassType", bound="CombinatorialClass")
CSSstrategy = Union["AbstractStrategy", "StrategyFactory"]

SpecificationClassesAndStrats = Tuple[
    List[Tuple[CombinatorialClassType, "AbstractStrategy"]],
    List[List[CombinatorialClassType]],
]

RulesDict = Dict[Label, Set[Tuple[Label, ...]]]


class WorkPacket(NamedTuple):
    label: Label
    strategies: Tuple[CSSstrategy, ...]
    inferral: bool


# From classdb
ClassKey = Union[bytes, CombinatorialClassType]
Key = Union[CombinatorialClassType, Label]

# From ruledb
SpecificationLabelsAndStrats = Tuple[
    List[Tuple[Label, "AbstractStrategy"]], List[List[Label]]
]
RuleKey = Tuple[Label, Tuple[Label, ...]]

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
