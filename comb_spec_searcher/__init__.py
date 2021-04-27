from typing import Optional

from .bijection import ParallelSpecFinder
from .comb_spec_searcher import CombinatorialSpecificationSearcher
from .combinatorial_class import CombinatorialClass, CombinatorialObject
from .isomorphism import Bijection
from .specification import CombinatorialSpecification
from .specification_drawer import ForestSpecificationDrawer, SpecificationDrawer
from .strategies import (
    AtomStrategy,
    CartesianProduct,
    CartesianProductStrategy,
    Constructor,
    DisjointUnion,
    DisjointUnionStrategy,
    Strategy,
    StrategyFactory,
    StrategyPack,
    SymmetryStrategy,
    VerificationStrategy,
)


def find_bijection_between(
    searcher1: CombinatorialSpecificationSearcher,
    searcher2: CombinatorialSpecificationSearcher,
) -> Optional[Bijection]:
    """Find bijections between two universes. If they are not of the same type, a
    custom atom comparator is needed."""
    specs = ParallelSpecFinder(searcher1, searcher2).find()
    return Bijection.construct(*specs) if specs else None


__version__ = "3.0.0"

__all__ = [
    "CombinatorialSpecificationSearcher",
    "CombinatorialClass",
    "CombinatorialObject",
    "CombinatorialSpecification",
    "ForestSpecificationDrawer",
    "SpecificationDrawer",
    "AtomStrategy",
    "CartesianProduct",
    "CartesianProductStrategy",
    "Constructor",
    "DisjointUnion",
    "DisjointUnionStrategy",
    "Strategy",
    "StrategyFactory",
    "StrategyPack",
    "SymmetryStrategy",
    "VerificationStrategy",
    "find_bijection_between",
]
