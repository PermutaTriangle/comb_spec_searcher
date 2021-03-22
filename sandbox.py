"""
Hook the forest db to load from a given universe.
"""
import time
from typing import Tuple

import sympy
from forests.forest import sympy_to_pumping_maple
from forests.packs import forest_pack
from tilings import Tiling
from tilings.strategies.verification import BasicVerificationStrategy
from tilings.tilescope import TileScope, TileScopePack

from comb_spec_searcher import rule_and_flip
from comb_spec_searcher.rule_db.forest import ForestRuleDB
from comb_spec_searcher.specification import CombinatorialSpecification
from comb_spec_searcher.specification_extrator import ForestRuleExtractor
from comb_spec_searcher.strategies.rule import AbstractRule


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
        for rule_key, shifts in rule_and_flip.all_flips(rule, self.classdb.get_label):
            self.forestdb.add_rule(rule_key, shifts)
        self.time_forest += time.time() - start
        if self.forestdb.is_pumping(self.start_label):
            self.spec_found()

    def spec_found(self) -> None:
        print(self.status(True))
        print("Forest found!")
        extractor = ForestRuleExtractor(
            self.start_label, self.forestdb, self.classdb, self.strategy_pack
        )
        spec = CombinatorialSpecification(
            self.classdb.get_class(self.start_label), extractor.rules()
        )
        import json

        with open("spec.json", "w") as fp:
            json.dump(spec.to_jsonable(), fp)
        json.dump
        spec.expand_verified()
        spec.sanity_check(4)
        spec.show()
        for n in range(10):
            print(spec.count_objects_of_size(n))
        raise ForestFoundError

    def status(self, elaborate: bool) -> str:
        s = f"Added from {self.num_rules} normal rules\n"
        s += f"Time spent on the forest stuff: {self.time_forest:.1f}\n"
        s += f"Size of the gap: {self.forestdb._gap_size}\n"
        s += f"Size of the stable subset: {self.forestdb._function._infinity_count}\n"
        s += f"Sizes of the pre-images: {self.forestdb._function._preimage_count}\n"
        s += self.classdb.status() + "\n"
        s += self.classqueue.status() + "\n"
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


css = SpecialSearcher(basis, pack)
try:
    css.auto_search(status_update=30)
except ForestFoundError:
    print(css.status(True))
    print(f"Forest found for root label {css.start_label}")
    assert css.get_specification is not None
