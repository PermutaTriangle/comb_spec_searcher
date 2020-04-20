from copy import copy
from itertools import chain
from typing import List, Optional

from ..utils import get_func_name

from .strategy import Strategy, StrategyGenerator


__all__ = "StrategyPack"


class StrategyPack:
    def __init__(
        self,
        initial_strats: List[StrategyGenerator],
        inferral_strats: List[Strategy],
        expansion_strats: List[List[StrategyGenerator]],
        ver_strats: List[Strategy],
        name: str,
        **kwargs
    ):
        self.name = name
        self.initial_strats = initial_strats
        self.inferral_strats = inferral_strats
        self.ver_strats = ver_strats
        self.expansion_strats = expansion_strats
        self.symmetries = kwargs.get("symmetries", [])
        self.iterative = kwargs.get("iterative", False)

    def __contains__(self, strategy: Strategy) -> bool:
        """
        Check if the pack contains a strategy.

        Two strategy from the same Strategy class are consider the same even if
        they have different parameter.
        """
        strats_in_pack = chain(
            self.initial_strats,
            self.ver_strats,
            self.inferral_strats,
            *self.expansion_strats,
        )
        return any(strat.__class__ == strategy.__class__ for strat in strats_in_pack)

    def __repr__(self) -> str:
        s = "{}(\n".format(self.__class__.__name__)
        s += "    initial_strats=[\n"
        for st in self.initial_strats:
            s += "        {!r},\n".format(st)
        s += "    ], ver_strats=[\n"
        for st in self.ver_strats:
            s += "        {!r},\n".format(st)
        s += "    ], inferral_strats=[\n"
        for st in self.inferral_strats:
            s += "        {!r},\n".format(st)
        s += "    ], expansion_strats=[\n"
        for sl in self.expansion_strats:
            s += "        [\n"
            for st in sl:
                s += "            {!r},\n".format(st)
            s += "        ],\n"
        s += "    ],\n"
        s += "    name={!r},\n".format(self.name)
        s += "    symmetries={!r},\n".format(self.symmetries)
        s += "    iterative={!r},\n".format(self.iterative)
        s += ")"
        return s

    def __str__(self) -> str:
        string = (
            "Looking for {} combinatorial specification" " with the strategies:\n"
        ).format("iterative" if self.iterative else "recursive")
        initial_strats = ", ".join(map(str, self.initial_strats))
        infer_strats = ", ".join(map(str, self.inferral_strats))
        verif_strats = ", ".join(map(str, self.ver_strats))
        string += "Inferral: {}\n".format(infer_strats)
        string += "Initial: {}\n".format(initial_strats)
        string += "Verification: {}\n".format(verif_strats)
        if self.symmetries:
            symme_strats = ", ".join(get_func_name(f) for f in self.symmetries)
            string += "Symmetries: {}\n".format(symme_strats)
        for i, strategies in enumerate(self.expansion_strats):
            strats = ", ".join(map(str, strategies))
            string += "Set {}: {}\n".format(i + 1, strats)
        return string

    def __eq__(self, other: object):
        if not isinstance(other, StrategyPack):
            return NotImplemented
        return self.__dict__ == other.__dict__

    def __copy__(self) -> "TileScopePack":
        return self.__class__(
            name=self.name,
            initial_strats=copy(self.initial_strats),
            ver_strats=copy(self.ver_strats),
            inferral_strats=copy(self.inferral_strats),
            expansion_strats=[copy(strat_list) for strat_list in self.expansion_strats],
            symmetries=copy(self.symmetries),
            iterative=self.iterative,
        )

    # JSON methods
    def to_jsonable(self) -> dict:
        return {
            "name": self.name,
            "initial_strats": [s.to_jsonable() for s in self.initial_strats],
            "inferral_strats": [s.to_jsonable() for s in self.inferral_strats],
            "ver_strats": [s.to_jsonable() for s in self.ver_strats],
            "expansion_strats": [
                [s.to_jsonable() for s in strat_list]
                for strat_list in self.expansion_strats
            ],
            "symmetries": self.symmetries,
            "iterative": self.iterative,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "StrategyPack":
        name = d.pop("name")
        initial_strats = [
            Strategy.from_dict(strat_dict) for strat_dict in d.pop("initial_strats")
        ]
        inferral_strats = [
            Strategy.from_dict(strat_dict) for strat_dict in d.pop("inferral_strats")
        ]
        ver_strats = [
            Strategy.from_dict(strat_dict) for strat_dict in d.pop("ver_strats")
        ]
        expansion_strats = [
            [Strategy.from_dict(strat_dict) for strat_dict in strat_list]
            for strat_list in d.pop("expansion_strats")
        ]
        return cls(
            initial_strats, inferral_strats, expansion_strats, ver_strats, name, **d
        )

    # Method to add power to a pack
    # Pack are immutable, these methods return a new pack.
    def add_initial(
        self, strategy: StrategyGenerator, name_ext: str = ""
    ) -> "StrategyPack":
        """
        Create a new pack with an additional initial strategy and append
        name_ext to the name of the pack.
        """
        if strategy in self:
            raise ValueError(
                ("The strategy {!r} is already in pack." "".format(strategy))
            )
        new_pack = copy(self)
        new_pack.initial_strats.append(strategy)
        if name_ext:
            new_pack.name = "_".join([self.name, name_ext])
        return new_pack

    def add_inferral(
        self, strategy: StrategyGenerator, name_ext: str = ""
    ) -> "StrategyPack":
        """
        Create a new pack with an additional inferral strategy and append
        name_ext to the name of the pack.
        """
        if strategy in self:
            raise ValueError(
                ("The strategy {!r} is already in pack." "".format(strategy))
            )
        new_pack = copy(self)
        new_pack.inferral_strats.append(strategy)
        if name_ext:
            new_pack.name = "_".join([self.name, name_ext])
        return new_pack

    def add_verification(
        self, strategy: StrategyGenerator, name_ext: str = ""
    ) -> "StrategyPack":
        """
        Create a new pack with an additional verification strategy and append
        name_ext to the name of the pack.
        """
        if strategy in self:
            raise ValueError(
                ("The strategy {!r} is already in pack." "".format(strategy))
            )
        new_pack = copy(self)
        new_pack.ver_strats.append(strategy)
        if name_ext:
            new_pack.name = "_".join([self.name, name_ext])
        return new_pack
