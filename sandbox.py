"""
Hook the forest db to load from a given universe.
"""
import json
import time
from datetime import timedelta
from typing import Tuple

import sympy
from forests.packs import forest_pack
from logzero import logger
from tilings import Tiling
from tilings.strategies.verification import LocallyFactorableVerificationStrategy
from tilings.tilescope import TileScope, TileScopePack

from comb_spec_searcher import rule_and_flip
from comb_spec_searcher.rule_db.forest import ForestRuleDB, RuleBucket
from comb_spec_searcher.specification import CombinatorialSpecification
from comb_spec_searcher.specification_extrator import ForestRuleExtractor
from comb_spec_searcher.strategies.rule import AbstractRule, Rule, VerificationRule
from comb_spec_searcher.strategies.strategy import EmptyStrategy


class ForestFoundError(Exception):
    pass


class SpecialSearcher(TileScope):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.forestdb = ForestRuleDB()
        self.time_forest = 0.0
        self.num_rules = 0

    def _add_rule(
        self, start_label: int, end_labels: Tuple[int, ...], rule: AbstractRule
    ) -> None:
        super()._add_rule(start_label, end_labels, rule)
        self.num_rules += 1
        start = time.time()
        flip_index = -2
        first_bucket = (
            RuleBucket.VERIFICATION
            if isinstance(rule, VerificationRule)
            else RuleBucket.NORMAL
        )
        for rule_key, shifts in rule_and_flip.all_flips(rule, self.classdb.get_label):
            flip_index += 1
            bucket = first_bucket if flip_index == -1 else RuleBucket.REVERSE
            self.forestdb.add_rule(rule_key, shifts, bucket)
            if self.forestdb.is_pumping(self.start_label):
                break
        self.time_forest += time.time() - start
        if self.forestdb.is_pumping(self.start_label):
            if flip_index == -1:
                critical_rule = rule
            else:
                assert isinstance(rule, Rule)
                assert rule.is_two_way()
                assert len(rule.children) > flip_index
                critical_rule = rule.to_reverse_rule(flip_index)
            logger.info("Critical rule found.")
            logger.info(critical_rule)
            self.spec_found()

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
# pack = pack.add_verification(BasicVerificationStrategy(), replace=True)
# basis = "132"

# Segmented
# pack = forest_pack
# basis = "0123_0132_0213_0231_1023_2013"

pack = TileScopePack.point_and_row_and_col_placements(row_only=True).make_fusion(
    isolation_level="isolated"
)
basis = "1423"

# Last 2x4
# basis = "1432_2143"
# pack = TileScopePack.point_placements()

pack.ver_strats = tuple(
    s
    for s in pack.ver_strats
    if not isinstance(s, LocallyFactorableVerificationStrategy)
)
pack = pack.add_verification(EmptyStrategy())

if __name__ == "__main__":
    css = SpecialSearcher(basis, pack)
    try:
        css.auto_search(status_update=60)
    except ForestFoundError:
        assert css.get_specification is not None
