from tilescopetwo.strategies import *
from comb_spec_searcher import StrategyPack

point_placement_super = StrategyPack(eq_strats=[all_point_placements],
                               ver_strats=[subset_verified],
                               inf_strats=[super_subobstruction_inferral],
                               other_strats=[[components], [all_cell_insertions]],
                               name="Point placements.")

point_placement = StrategyPack(eq_strats=[all_point_placements],
                               ver_strats=[subset_verified],
                               inf_strats=[subobstruction_inferral],
                               other_strats=[[components], [all_cell_insertions]],
                               name="Point placements.")
