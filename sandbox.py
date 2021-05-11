"""
Hook the forest db to load from a given universe.
"""
import json
import time
from datetime import timedelta
from typing import Set, Tuple

import sympy
from forests.packs import forest_pack
from logzero import logger
from tilings import Tiling
from tilings.strategies import LocallyFactorableVerificationStrategy
from tilings.tilescope import TileScope, TileScopePack

from comb_spec_searcher.rule_db.forest import RuleDBForest
from comb_spec_searcher.specification import CombinatorialSpecification
from comb_spec_searcher.specification_extrator import ForestRuleExtractor
from comb_spec_searcher.strategies.rule import AbstractRule, Rule
from comb_spec_searcher.strategies.strategy import EmptyStrategy


class ForestFoundError(Exception):
    pass


class SpecialSearcher(TileScope):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.forestdb: RuleDBForest = RuleDBForest()
        self.time_forest: float = 0.0
        self.num_rules: int = 0
        self.already_empty: Set[int] = set()

    def _add_rule(
        self, start_label: int, end_labels: Tuple[int, ...], rule: AbstractRule
    ) -> None:
        super()._add_rule(start_label, end_labels, rule)
        self.num_rules += 1
        start = time.time()
        new_rules = [rule]
        if rule.is_reversible():
            assert isinstance(rule, Rule)
            new_rules.extend(rule.to_reverse_rule(i) for i in range(len(rule.children)))
        for rule in new_rules:
            self.forestdb.add_rule(rule.forest_key(self.classdb.get_label))
            if self.forestdb.is_pumping(self.start_label):
                break
        self.time_forest += time.time() - start
        if self.forestdb.is_pumping(self.start_label):
            logger.info("Critical rule found.")
            logger.info(rule)
            self.spec_found()

    def is_empty(self, comb_class: Tiling, label: int) -> bool:
        empty = super().is_empty(comb_class, label)
        if empty and label not in self.already_empty:
            self.already_empty.add(label)
            empty_strat: EmptyStrategy = EmptyStrategy()
            empty_rule = empty_strat(comb_class)
            self._add_rule(label, (), empty_rule)
        return empty

    def spec_found(self) -> None:
        logger.info("Forest found!\n" + self.status(True))
        extractor = ForestRuleExtractor(
            self.start_label, self.forestdb, self.classdb, self.strategy_pack
        )
        extractor.check()
        spec = CombinatorialSpecification(
            self.classdb.get_class(self.start_label), extractor.rules()
        )
        with open("spec.json", "w") as fp:
            json.dump(spec.to_jsonable(), fp)
        spec.show()
        raise ForestFoundError

    def status(self, elaborate: bool) -> str:
        s = super().status(elaborate)
        s += "\nForest status:\n"
        s += f"\tAdded from {self.num_rules} normal rules\n"
        s += f"\tTime spent on the forest stuff: {timedelta(seconds=int(self.time_forest))}\n"
        s += f"\tSize of the gap: {self.forestdb._gap_size}\n"
        s += f"\tSize of the stable subset: {self.forestdb._function._infinity_count}\n"
        s += f"\tSizes of the pre-images: {self.forestdb._function._preimage_count}\n"
        return s

    def get_function(self, comb_class: Tiling) -> sympy.Function:
        """
        Return a sympy function for the comb class, using the label it is
        assigned.
        """
        x = sympy.var("x")
        extra_parameters = [sympy.var(k) for k in comb_class.extra_parameters]
        return sympy.Function("F_{}".format(self.classdb.get_label(comb_class)))(
            x, *extra_parameters
        )


# pack = TileScopePack.point_placements()
# basis = "132"

# Segmented
# pack = forest_pack
# basis = "0123_0132_0213_0231_1023_2013"

# pack = TileScopePack.point_and_row_and_col_placements(row_only=True).make_fusion(
#     isolation_level="isolated"
# )
# basis = "1423"

# Last 2x4
# basis = "1432_2143"
# pack = TileScopePack.point_placements()

basis = "0132_1023"
pack = TileScopePack.point_and_row_and_col_placements(row_only=True).make_fusion(
    isolation_level="isolated"
)

if __name__ == "__main__":
    css = SpecialSearcher(basis, pack)
    try:
        spec = css.auto_search(status_update=60)
    except ForestFoundError:
        pass
    else:
        spec.show()
