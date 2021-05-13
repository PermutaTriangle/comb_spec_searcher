"""
Hook the forest db to load from a given universe.
"""

from typing import Dict, Tuple

from forests.packs import forest_pack
from tilings.tilescope import TileScope, TileScopePack

from comb_spec_searcher.rule_db import RuleDBForest
from comb_spec_searcher.specification_drawer import (
    ForestSpecificationDrawer,
    SpecificationDrawer,
)

d: Dict[str, Tuple["str", TileScopePack]] = {
    "132": ("132", TileScopePack.point_placements()),
    "segmented": ("0123_0132_0213_0231_1023_2013", forest_pack),
    "1423": (
        "1423",
        TileScopePack.point_and_row_and_col_placements(row_only=True).make_fusion(
            isolation_level="isolated"
        ),
    ),
    "last_2x4": (
        "1432_2143",
        TileScopePack.point_and_row_and_col_placements(row_only=True).make_fusion(
            isolation_level="isolated"
        ),
    ),
    "small2x4": (
        "0132_1023",
        TileScopePack.point_and_row_and_col_placements(row_only=True).make_fusion(
            isolation_level="isolated"
        ),
    ),
}


def run_example(key: str) -> None:
    basis, pack = d[key]
    css = TileScope(basis, pack, ruledb=RuleDBForest())
    spec = css.auto_search(status_update=30)
    spec.show()


def iso_forest():
    pack = TileScopePack.only_root_placements(2, 1)
    bases = ["0231_2031", "0132_1032", "0231_0321"]
    searchers = [TileScope(b, pack, ruledb=RuleDBForest()) for b in bases]
    specs = [css.auto_search() for css in searchers]
    drawers = [SpecificationDrawer(spec) for spec in specs]
    forest_drawer = ForestSpecificationDrawer(drawers)
    forest_drawer.show()
    forest_drawer.share()
    for spec in specs:
        spec.expand_verified()
    for spec in specs:
        print([spec.count_objects_of_size(n) for n in range(10)])


if __name__ == "__main__":
    iso_forest()
