from tilescopetwo.strategies import *
from atrapstrategypack import ATRAPStrategyPack
from functools import partial
from permuta import Perm

# WARNING: To use full subobstruction inferral need strategy
# 'subobstruction_inferral_rec' but it is a lot slower. The function
# 'subobstruction_inferral' is a subset of the work.

point_placement = ATRAPStrategyPack(
         eq_strats=[all_point_placements],
         ver_strats=[subset_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[components], [all_cell_insertions]],
         name="point_placement")

point_placement_one_cell_inferral = ATRAPStrategyPack(
         eq_strats=[all_point_placements],
         ver_strats=[subset_verified],
         inf_strats=[empty_cell_inferral],
         other_strats=[[components], [all_cell_insertions]],
         name="point_placement")

point_placement_no_infer = ATRAPStrategyPack(
         eq_strats=[all_point_placements],
         ver_strats=[subset_verified],
         inf_strats=[empty_cell_inferral],
         other_strats=[[components], [all_cell_insertions]],
         name="point_placement_no_infer")

row_placements_only = ATRAPStrategyPack(
         eq_strats=[],
         ver_strats=[subset_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[components],[all_cell_insertions, row_placements]],
         name="row_placements")

col_placements_only = ATRAPStrategyPack(
         eq_strats=[],
         ver_strats=[subset_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[components], [all_cell_insertions, col_placements]],
         name="col_placements")

row_and_column_placements = ATRAPStrategyPack(
         eq_strats=[],
         ver_strats=[subset_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[components],
                       [all_cell_insertions, row_placements, col_placements]],
         name="row_and_column_placements")

row_and_column_placements_and_database = ATRAPStrategyPack(
         eq_strats=[],
         ver_strats=[subset_verified, database_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[components],
                       [all_cell_insertions, row_placements, col_placements]],
         name="row_and_column_placements_and_database")

point_separation_and_row_col_placements = ATRAPStrategyPack(
         eq_strats=[point_separation],
         ver_strats=[subset_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[components],
                       [all_cell_insertions,
                        partial(row_placements, all_positive_in_row=False),
                        partial(col_placements, all_positive_in_col=False)]],
         name="row_and_column_placements")

binary_force_only = ATRAPStrategyPack(
    eq_strats=[forced_binary_pattern],
    ver_strats=[subset_verified],
    inf_strats=[empty_cell_inferral, row_and_column_separation],
    other_strats=[[partial(components, unions=True)],
                  [all_cell_insertions],
                  [partial(all_requirement_insertions, maxreqlength=4)],
                  ],
    name="binary_force w/ row-col separation and cell insertions")

point_separation_and_isolation = ATRAPStrategyPack(
         eq_strats=[point_separation],
         ver_strats=[subset_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[partial(components, workable=False, unions=True)],
                       [all_cell_insertions, point_isolations]],
         name="point_separation_and_isolation")
