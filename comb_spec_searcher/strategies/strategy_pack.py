"""
A class for containing the set of strategies that
CombinatorialSpecificationSearcher (CSS) should apply when searching for a
CombinatorialSpecification.

The default setting treats the pack as follows:
    - inferral:     These srategies are applied to every comb_class first when
                    found. They should all be equivalence strategies and if a
                    strategy returns a rule, then we only work from the child.
    - initial:      After inferral we apply all of the initial strategies to
                    a comb_class. After the initial strategies are applied, the
                    the comb_class is added to the next queue, waiting for the
                    level to change (when the next becomes curr).
    - expansion:    The expansion strategies are set of sets of strategies
                    S1, ..., Sk. The strategies S1 are applied to all
                    comb_class in curr queue, then S2 to all, then S3, etc,
                    until all of the strategies are applied.
    - verification: A verification strategy is applied to every comb_class when
                    it is first found.
    - symmetry:     Symmetries are applied to a comb_class when it is first
                    found.
(the above settings can be edited by creating an alternative CSSQueue class)

If the iterative boolean is True, then CSS will search for an iterative
specification.
"""
from itertools import chain
from typing import Iterable, Iterator, Optional, Type, TypeVar

from .strategy import CSSstrategy, Strategy

PackType = TypeVar("PackType", bound="StrategyPack")

__all__ = ["StrategyPack"]


class StrategyPack:
    """
    A pack used by CSS to guide how to search for a specification.
    """

    def __init__(
        self,
        initial_strats: Iterable[CSSstrategy],
        inferral_strats: Iterable[CSSstrategy],
        expansion_strats: Iterable[Iterable[CSSstrategy]],
        ver_strats: Iterable[CSSstrategy],
        name: str,
        symmetries: Iterable[CSSstrategy] = None,
        iterative: bool = False,
    ):
        self.name = name
        self.initial_strats = tuple(initial_strats)
        self.inferral_strats = tuple(inferral_strats)
        self.ver_strats = tuple(ver_strats)
        self.expansion_strats = tuple(tuple(x) for x in expansion_strats)
        self.symmetries = tuple(symmetries) if symmetries is not None else tuple()
        self.iterative = iterative

    def __iter__(self) -> Iterator[CSSstrategy]:
        """Iterator over all the strategies in the pack."""
        return chain(
            self.initial_strats,
            self.ver_strats,
            self.inferral_strats,
            self.symmetries,
            *self.expansion_strats,
        )

    def __contains__(self, strategy: CSSstrategy) -> bool:
        """
        Check if the pack contains a strategy.

        Two strategy from the same Strategy class are consider the same even if
        they have different parameter.
        """
        return any(strat.__class__ == strategy.__class__ for strat in self)

    def __repr__(self) -> str:
        s = f"{self.__class__.__name__}(\n"
        s += "    initial_strats=[\n"
        for st in self.initial_strats:
            s += f"        {st!r},\n"
        s += "    ], ver_strats=[\n"
        for st in self.ver_strats:
            s += f"        {st!r},\n"
        s += "    ], inferral_strats=[\n"
        for st in self.inferral_strats:
            s += f"        {st!r},\n"
        s += "    ], expansion_strats=[\n"
        for sl in self.expansion_strats:
            s += "        [\n"
            for st in sl:
                s += f"            {st!r},\n"
            s += "        ],\n"
        s += "    ],\n"
        s += f"    name={self.name!r},\n"
        s += f"    symmetries={self.symmetries!r},\n"
        s += f"    iterative={self.iterative!r},\n"
        s += ")"
        return s

    def __str__(self) -> str:
        type_search = "iterative" if self.iterative else "recursive"
        string = (
            f"Looking for {type_search} combinatorial specification"
            " with the strategies:\n"
        )
        initial_strats = ", ".join(map(str, self.initial_strats))
        infer_strats = ", ".join(map(str, self.inferral_strats))
        verif_strats = ", ".join(map(str, self.ver_strats))
        string += f"Inferral: {infer_strats}\n"
        string += f"Initial: {initial_strats}\n"
        string += f"Verification: {verif_strats}\n"
        if self.symmetries:
            symme_strats = ", ".join(map(str, self.symmetries))
            string += f"Symmetries: {symme_strats}\n"
        for i, strategies in enumerate(self.expansion_strats):
            strats = ", ".join(map(str, strategies))
            string += f"Set {i+1}: {strats}\n"
        return string

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StrategyPack):
            return NotImplemented
        return self.__dict__ == other.__dict__

    # JSON methods
    def to_jsonable(self) -> dict:
        """
        Return a JSON serializable dictionary.
        """
        return {
            "name": self.name,
            "initial_strats": [s.to_jsonable() for s in self.initial_strats],
            "inferral_strats": [s.to_jsonable() for s in self.inferral_strats],
            "ver_strats": [s.to_jsonable() for s in self.ver_strats],
            "expansion_strats": [
                [s.to_jsonable() for s in strat_list]
                for strat_list in self.expansion_strats
            ],
            "symmetries": [s.to_jsonable() for s in self.symmetries],
            "iterative": self.iterative,
        }

    @classmethod
    def from_dict(cls: Type[PackType], d: dict) -> PackType:
        """
        Return a StrategyPack from the dict object return by the to_jsonable method.
        """
        name = d["name"]
        initial_strats = [
            Strategy.from_dict(strat_dict) for strat_dict in d["initial_strats"]
        ]
        inferral_strats = [
            Strategy.from_dict(strat_dict) for strat_dict in d["inferral_strats"]
        ]
        ver_strats = [Strategy.from_dict(strat_dict) for strat_dict in d["ver_strats"]]
        expansion_strats = [
            [Strategy.from_dict(strat_dict) for strat_dict in strat_list]
            for strat_list in d["expansion_strats"]
        ]
        symmetries = (
            [Strategy.from_dict(strat_dict) for strat_dict in d["symmetries"]]
            if "symmetries" in d
            else []
        )
        return cls(
            initial_strats,
            inferral_strats,
            expansion_strats,
            ver_strats,
            name,
            symmetries=symmetries,
            iterative=d.get("iterative", False),
        )

    # Method to add power to a pack
    # Pack are immutable, these methods return a new pack.
    def add_initial(
        self: PackType, strategy: CSSstrategy, name_ext: str = "", apply_first=False
    ) -> PackType:
        """
        Create a new pack with an additional initial strategy and append
        name_ext to the name of the pack.
        """
        if strategy in self:
            raise ValueError(f"The strategy {strategy!r} is already in pack.")
        if apply_first:
            initial_strats = (strategy,) + self.initial_strats
        else:
            initial_strats = self.initial_strats + (strategy,)
        return self.__class__(
            name="_".join([self.name, name_ext]) if name_ext else self.name,
            initial_strats=initial_strats,
            ver_strats=self.ver_strats,
            inferral_strats=self.inferral_strats,
            expansion_strats=self.expansion_strats,
            symmetries=self.symmetries,
            iterative=self.iterative,
        )

    def add_inferral(
        self: PackType, strategy: CSSstrategy, name_ext: str = ""
    ) -> PackType:
        """
        Create a new pack with an additional inferral strategy and append
        name_ext to the name of the pack.
        """
        if strategy in self:
            raise ValueError(f"The strategy {strategy!r} is already in pack.")
        return self.__class__(
            name="_".join([self.name, name_ext]) if name_ext else self.name,
            initial_strats=self.initial_strats,
            ver_strats=self.ver_strats,
            inferral_strats=self.inferral_strats + (strategy,),
            expansion_strats=self.expansion_strats,
            symmetries=self.symmetries,
            iterative=self.iterative,
        )

    def add_expansion(
        self: PackType,
        strategies: Iterable[CSSstrategy],
        idx: Optional[int] = None,
        name_ext: str = "",
    ) -> PackType:
        """
        Create a new pack with the expansion strategies added as a new set.
        If idx is given as an argument, then the strategies are appended to
        Set idx in the expansion strategies.
        Adds name_ext to the name of the pack.
        """
        strategies = tuple(strategies)
        for strat in strategies:
            if strat in self:
                raise ValueError(f"The strategy {strat!r} is already in the pack")
        if idx is None:
            expansion_strats = self.expansion_strats + (strategies,)
        else:
            try:
                expansion_strats = (
                    self.expansion_strats[:idx]
                    + (self.expansion_strats[idx] + strategies,)
                    + self.expansion_strats[idx + 1 :]
                )
            except IndexError as error:
                raise IndexError("expansion_strats: index out of range") from error
        return self.__class__(
            name="_".join([self.name, name_ext]) if name_ext else self.name,
            initial_strats=self.initial_strats,
            ver_strats=self.ver_strats,
            inferral_strats=self.inferral_strats,
            expansion_strats=expansion_strats,
            symmetries=self.symmetries,
            iterative=self.iterative,
        )

    def add_symmetry(
        self: PackType, strategy: CSSstrategy, name_ext: str = ""
    ) -> PackType:
        """
        Create a new pack with an additional symmetry strategy and append
        name_ext to the name of the pack.
        """
        if strategy in self:
            raise ValueError(f"The strategy {strategy!r} is already in pack.")
        return self.__class__(
            name="_".join([self.name, name_ext]) if name_ext else self.name,
            initial_strats=self.initial_strats,
            ver_strats=self.ver_strats,
            inferral_strats=self.inferral_strats,
            expansion_strats=self.expansion_strats,
            symmetries=self.symmetries + (strategy,),
            iterative=self.iterative,
        )

    def add_verification(
        self: PackType,
        strategy: CSSstrategy,
        name_ext: str = "",
        replace: bool = False,
        apply_first: bool = False,
    ) -> PackType:
        """
        Create a new pack with an additional verification strategy and append
        name_ext to the name of the pack.
        If replace is set, it will ignore old verification strategies
        """
        if not replace and strategy in self:
            raise ValueError(f"The strategy {strategy!r} is already in pack.")
        if apply_first:
            ver_strats = (strategy,) + (tuple() if replace else self.ver_strats)
        else:
            ver_strats = (tuple() if replace else self.ver_strats) + (strategy,)
        return self.__class__(
            name="_".join([self.name, name_ext]) if name_ext else self.name,
            initial_strats=self.initial_strats,
            ver_strats=ver_strats,
            inferral_strats=self.inferral_strats,
            expansion_strats=self.expansion_strats,
            symmetries=self.symmetries,
            iterative=self.iterative,
        )

    def remove_strategy(self, strategy: CSSstrategy):
        """Create a new pack where the strategy is removed."""
        d = strategy.to_jsonable()

        def replace_list(strats):
            """Return a new list with the replaced fusion strat."""
            res = []
            for strategy in strats:
                if not strategy.to_jsonable() == d:
                    res.append(strategy)
            return res

        return self.__class__(
            ver_strats=replace_list(self.ver_strats),
            inferral_strats=replace_list(self.inferral_strats),
            initial_strats=replace_list(self.initial_strats),
            expansion_strats=[
                strat for strat in map(replace_list, self.expansion_strats) if strat
            ],
            name=self.name,
            symmetries=replace_list(self.symmetries),
            iterative=self.iterative,
        )

    def make_iterative(self: PackType, name_ext: str = "") -> PackType:
        """
        Create a new pack with same strategies but iterative
        """
        return self.__class__(
            name="_".join([self.name, name_ext]) if name_ext else self.name,
            initial_strats=self.initial_strats,
            ver_strats=self.ver_strats,
            inferral_strats=self.inferral_strats,
            expansion_strats=self.expansion_strats,
            symmetries=self.symmetries,
            iterative=True,
        )
