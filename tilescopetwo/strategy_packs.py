from tilescopetwo.strategies import *
from comb_spec_searcher import StrategyPack
from functools import partial

# WARNING: To use full subobstruction inferral need strategy
# 'subobstruction_inferral_rec' but it is a lot slower. The function
# 'subobstruction_inferral' is a subset of the work.

point_placement_with_subobstruction_inferral = StrategyPack(
         eq_strats=[all_point_placements],
         ver_strats=[subset_verified],
         inf_strats=[subobstruction_inferral, row_and_column_separation],
         other_strats=[[components], [all_cell_insertions]],
         name="point_placement_with_subobstruction_inferral")

point_placement_one_cell_inferral = StrategyPack(
         eq_strats=[all_point_placements],
         ver_strats=[subset_verified],
         inf_strats=[subobstruction_inferral],
         other_strats=[[components], [all_cell_insertions]],
         name="point_placement_one_cell_inferral")

point_placement_no_infer = StrategyPack(
         eq_strats=[all_point_placements],
         ver_strats=[subset_verified],
         inf_strats=[],
         other_strats=[[components], [all_cell_insertions]],
         name="point_placement_no_infer")

row_placements_with_subobstruction_inferral = StrategyPack(
         eq_strats=[],
         ver_strats=[subset_verified],
         inf_strats=[subobstruction_inferral, row_and_column_separation],
         other_strats=[[components],[all_cell_insertions, row_placements]],
         name="row_placements_with_subobstruction_inferral")

col_placements_with_subobstruction_inferral = StrategyPack(
         eq_strats=[],
         ver_strats=[subset_verified],
         inf_strats=[subobstruction_inferral, row_and_column_separation],
         other_strats=[[components], [all_cell_insertions, col_placements]],
         name="col_placements_with_subobstruction_inferral")

row_and_column_placements_with_subobstruction_inferral = StrategyPack(
         eq_strats=[],
         ver_strats=[subset_verified],
         inf_strats=[subobstruction_inferral, row_and_column_separation],
         other_strats=[[components],
                       [all_cell_insertions, row_placements, col_placements]],
         name="row_and_column_placements_with_subobstruction_inferral")

row_and_column_placements_with_subobstruction_inferral_and_database = StrategyPack(
         eq_strats=[],
         ver_strats=[subset_verified, database_verified],
         inf_strats=[subobstruction_inferral, row_and_column_separation],
         other_strats=[[components],
                       [all_cell_insertions, row_placements, col_placements]],
         name="row_and_column_placements_with_subobstruction_inferral_and_database")

point_separation_and_row_col_placements = StrategyPack(
         eq_strats=[point_separation],
         ver_strats=[subset_verified],
         inf_strats=[subobstruction_inferral, row_and_column_separation],
         other_strats=[[components],
                       [all_cell_insertions,
                        partial(row_placements, all_positive_in_row=False),
                        partial(col_placements, all_positive_in_col=False)]],
         name="row_and_column_placements_with_subobstruction_inferral")

# binary_force = StrategyPack(
    # eq_strats=[all_point_placements],
    # ver_strats=[subset_verified],
    # inf_strats=[subobstruction_inferral],
    # other_strats=[[components], [all_cell_insertions],
                  # [partial(forced_binary_pattern, maxlen=3, forcelen=2)]],
    # name="binary_force")

binary_force = StrategyPack(
    eq_strats=[all_point_placements],
    ver_strats=[subset_verified, database_verified],
    inf_strats=[subobstruction_inferral],
    other_strats=[[components], [all_cell_insertions],
                  [forced_binary_pattern]],
    name="binary_force")

binary_force_rowcolsep = StrategyPack(
    eq_strats=[],
    ver_strats=[subset_verified],
    inf_strats=[subobstruction_inferral, row_and_column_separation],
    other_strats=[[components], [all_cell_insertions, row_placements, col_placements],
                  [forced_binary_pattern]],
    name="binary_force w/ row-col separation")

binary_force_rowcolsep_database = StrategyPack(
    eq_strats=[],
    ver_strats=[subset_verified, database_verified],
    inf_strats=[subobstruction_inferral, row_and_column_separation],
    other_strats=[[components], [all_cell_insertions, row_placements, col_placements],
                  [forced_binary_pattern]],
    name="binary_force w/ row-col separation and database verification")

# binary_force_rowcolsep_subobrec = StrategyPack(
#     eq_strats=[],
#     ver_strats=[subset_verified],
#     inf_strats=[subobstruction_inferral, row_and_column_separation],
#     other_strats=[[components], [all_cell_insertions, row_placements, col_placements],
#                   [forced_binary_pattern]],
#     name="binary_force w/ row-col separation, recursive subob inferral")
