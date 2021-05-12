"""
Hook the forest db to load from a given universe.
"""

from typing import Dict, Tuple

from forests.packs import forest_pack
from tilings.tilescope import TileScope, TileScopePack

from comb_spec_searcher.rule_db import RuleDBForest

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

if __name__ == "__main__":
    basis, pack = d["1423"]
    css = TileScope(basis, pack, ruledb=RuleDBForest())
    spec = css.auto_search(status_update=30)
    spec.show()
