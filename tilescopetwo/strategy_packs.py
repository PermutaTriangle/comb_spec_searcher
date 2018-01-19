from tilescopetwo.strategies import *
from comb_spec_searcher import StrategyPack
from functools import partial
from permuta import Perm

# WARNING: To use full subobstruction inferral need strategy
# 'subobstruction_inferral_rec' but it is a lot slower. The function
# 'subobstruction_inferral' is a subset of the work.

################################################################################
###################### STRATEGY PACKS FOR RUN 15/11/2017 #######################
################################################################################

forced_patterns_3 = StrategyPack(
        eq_strats=[],
        ver_strats=[subset_verified, database_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True)],
                      [partial(all_requirement_insertions, maxreqlen=3),
                       all_cell_insertions, forced_binary_pattern]],
        name="forced_patterns_3")

forced_patterns_3_with_row_column_placements = StrategyPack(
        eq_strats=[],
        ver_strats=[subset_verified, database_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True)],
                      [partial(all_requirement_insertions, maxreqlen=3),
                       all_cell_insertions, row_placements, col_placements,
                       forced_binary_pattern]],
        name="forced_patterns_3_with_row_column_placements")

row_column_placements = StrategyPack(
        eq_strats=[],
        ver_strats=[subset_verified, database_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [all_cell_insertions, row_placements,  col_placements]],
        name="row_column_placements")

point_sep_and_iso = StrategyPack(
        eq_strats=[point_separation],
        ver_strats=[subset_verified, database_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True, workable=False)],
                      [all_cell_insertions, point_isolations]],
        name="point_sep_and_iso")

forced_patterns_4 = StrategyPack(
        eq_strats=[],
        ver_strats=[subset_verified, database_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True)],
                      [partial(all_requirement_insertions, maxreqlen=4),
                       all_cell_insertions,
                       forced_binary_pattern]],
        name="forced_patterns_4")

################################################################################
################################################################################
###################### STRATEGY PACKS FOR RUN 21/11/2017 #######################
################################################################################

root_requirement_placements_3 = StrategyPack(
        eq_strats=[],
        ver_strats=[subset_verified, database_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [partial(root_requirement_insertions, maxreqlen=3),
                       forced_binary_pattern],
                      [all_cell_insertions, row_placements,  col_placements]],
        name="root_requirement_placements_3")

root_requirement_placements_4 = StrategyPack(
        eq_strats=[],
        ver_strats=[subset_verified, database_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [partial(root_requirement_insertions, maxreqlen=4),
                       forced_binary_pattern],
                      [all_cell_insertions, row_placements,  col_placements]],
        name="root_requirement_placements_4")

root_requirement_placements_3_point_placements = StrategyPack(
        eq_strats=[all_point_placements],
        ver_strats=[subset_verified, database_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [partial(root_requirement_insertions, maxreqlen=3),
                       forced_binary_pattern],
                      [all_cell_insertions]],
        name="root_requirement_placements_3_point_placements")

root_requirement_placements_4_point_placements = StrategyPack(
        eq_strats=[all_point_placements],
        ver_strats=[subset_verified, database_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [partial(root_requirement_insertions, maxreqlen=4),
                       forced_binary_pattern],
                      [all_cell_insertions]],
        name="root_requirement_placements_4_point_placements")

point_placement = StrategyPack(
         eq_strats=[all_point_placements],
         ver_strats=[subset_verified, database_verified, globally_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[components], [all_cell_insertions]],
         name="point_placement")

point_sep_equiv_iso = StrategyPack(
        eq_strats=[point_separation,
                   partial(point_isolations, equivalence_only=True)],
        ver_strats=[subset_verified, database_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True, workable=False)],
                      [all_cell_insertions,
                       partial(point_isolations, ignore_equivalence=True)]],
        name="point_sep_equiv_iso")

row_column_eqv_placements = StrategyPack(
        eq_strats=[partial(row_placements, equivalence_only=True),
                   partial(col_placements, equivalence_only=True)],
        ver_strats=[subset_verified, database_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [all_cell_insertions,
                       partial(row_placements, ignore_equivalence=True),
                       partial(col_placements, ignore_equivalence=True)]],
        name="row_column_eqv_placements")

all_strategies_no_req = StrategyPack(
        eq_strats=[all_point_placements, point_separation,
                   partial(row_placements, equivalence_only=True),
                   partial(col_placements, equivalence_only=True),
                   partial(point_isolations, equivalence_only=True)],
         ver_strats=[subset_verified, database_verified, globally_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[partial(components, unions=True)],
                       [all_cell_insertions,
                        partial(row_placements, ignore_equivalence=True),
                        partial(col_placements, ignore_equivalence=True),
                        partial(point_isolations, ignore_equivalence=True)]],
        name="all_strategies_no_req")

all_strategies = StrategyPack(
        eq_strats=[all_point_placements, point_separation,
                   partial(row_placements, equivalence_only=True),
                   partial(col_placements, equivalence_only=True),
                   partial(point_isolations, equivalence_only=True)],
         ver_strats=[subset_verified, database_verified, globally_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[partial(components, unions=True)],
                       [partial(all_requirement_insertions, maxreqlen=4),
                        forced_binary_pattern],
                       [all_cell_insertions,
                        partial(row_placements, ignore_equivalence=True),
                        partial(col_placements, ignore_equivalence=True),
                        partial(point_isolations, ignore_equivalence=True)]],
        name="all_strategies")

################################################################################
################################################################################
###################### STRATEGY PACKS FOR RUN 04/12/2017 #######################
################################################################################

# root_requirement_placements_5, point_placement, row_column_placements,
# row_column_eqv_placements, point_sep_and_iso, point_sep_equiv_iso,
# root_requirement_placements_4, root_requirement_placements_5,
# forced_patterns_3_with_row_column_placements,
# forced_patterns_4_with_row_column_placements, all_strategies_no_req,
# all_strategies_no_req_no_eqv

root_requirement_placements_5 = StrategyPack(
        eq_strats=[],
        ver_strats=[subset_verified, database_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [partial(root_requirement_insertions, maxreqlen=5),
                       forced_binary_pattern],
                      [all_cell_insertions, row_placements,  col_placements]],
        name="root_requirement_placements_5")

forced_patterns_4_with_row_column_placements = StrategyPack(
        eq_strats=[],
        ver_strats=[subset_verified, database_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True)],
                      [partial(all_requirement_insertions, maxreqlen=4),
                       all_cell_insertions, row_placements, col_placements,
                       forced_binary_pattern]],
        name="forced_patterns_4_with_row_column_placements")

all_strategies_no_req_no_eqv = StrategyPack(
        eq_strats=[],
         ver_strats=[subset_verified, database_verified, globally_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[partial(components, unions=True)],
                       [all_cell_insertions, all_point_placements,
                        point_separation, row_placements, col_placements,
                        point_isolations]],
        name="all_strategies_no_req_no_eqv")

################################################################################
################################################################################
###################### STRATEGY PACKS FOR RUN 21/12/2017 #######################
################################################################################

# SYMMETRY FLAG TURNED TO TRUE

# point_placement, row_column_placements,
# row_column_eqv_placements, point_sep_and_iso, point_sep_equiv_iso,
# root_requirement_placements_4,
# forced_patterns_3_with_row_column_placements,
# forced_patterns_4_with_row_column_placements, all_strategies_no_req,
# all_strategies_no_req_no_eqv

forced_patterns_3_with_point_placements = StrategyPack(
        eq_strats=[all_point_placements],
        ver_strats=[subset_verified, database_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True)],
                      [partial(all_requirement_insertions, maxreqlen=3),
                       all_cell_insertions, forced_binary_pattern]],
        name="forced_patterns_3_with_point_placements")

forced_patterns_4_with_point_placements = StrategyPack(
        eq_strats=[all_point_placements],
        ver_strats=[subset_verified, database_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True)],
                      [partial(all_requirement_insertions, maxreqlen=4),
                       all_cell_insertions, forced_binary_pattern]],
        name="forced_patterns_4_with_point_placements")

point_sep_and_iso_no_unions = StrategyPack(
        eq_strats=[point_separation],
        ver_strats=[subset_verified, database_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [all_cell_insertions, point_isolations]],
        name="point_sep_and_iso_no_unions")

point_sep_equiv_iso_no_unions = StrategyPack(
        eq_strats=[point_separation,
                   partial(point_isolations, equivalence_only=True)],
        ver_strats=[subset_verified, database_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [all_cell_insertions,
                       partial(point_isolations, ignore_equivalence=True)]],
        name="point_sep_equiv_iso_no_unions")

################################################################################
################################################################################
###################### point interleaving strategy packs #######################
################################################################################

# SYMMETRY FLAG TURNED TO FALSE!!!!!!!

point_placement_pi = StrategyPack(
         eq_strats=[all_point_placements],
         ver_strats=[subset_verified, globally_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[partial(components, point_interleaving=True)],
                       [all_cell_insertions]],
         name="point_placement_pi")

row_column_placements_pi = StrategyPack(
        eq_strats=[],
        ver_strats=[subset_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, point_interleaving=True)],
                      [all_cell_insertions, row_placements,  col_placements]],
        name="row_column_placements_pi")

row_column_eqv_placements_pi = StrategyPack(
        eq_strats=[partial(row_placements, equivalence_only=True),
                   partial(col_placements, equivalence_only=True)],
        ver_strats=[subset_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, point_interleaving=True)],
                      [all_cell_insertions,
                       partial(row_placements, ignore_equivalence=True),
                       partial(col_placements, ignore_equivalence=True)]],
        name="row_column_eqv_placements_pi")

point_sep_and_iso_pi = StrategyPack(
        eq_strats=[point_separation],
        ver_strats=[subset_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True,
                               point_interleaving=True, workable=False)],
                      [all_cell_insertions, point_isolations]],
        name="point_sep_and_iso_pi")

point_sep_equiv_iso_pi = StrategyPack(
        eq_strats=[point_separation,
                   partial(point_isolations, equivalence_only=True)],
        ver_strats=[subset_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True,
                               workable=False, point_interleaving=True)],
                      [all_cell_insertions,
                       partial(point_isolations, ignore_equivalence=True)]],
        name="point_sep_equiv_iso_pi")

root_requirement_placements_3_pi = StrategyPack(
        eq_strats=[],
        ver_strats=[subset_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, point_interleaving=True)],
                      [partial(root_requirement_insertions, maxreqlen=3),
                       forced_binary_pattern],
                      [all_cell_insertions, row_placements,  col_placements]],
        name="root_requirement_placements_3_pi")

root_requirement_placements_4_pi = StrategyPack(
        eq_strats=[],
        ver_strats=[subset_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, point_interleaving=True)],
                      [partial(root_requirement_insertions, maxreqlen=4),
                       forced_binary_pattern],
                      [all_cell_insertions, row_placements,  col_placements]],
        name="root_requirement_placements_4_pi")

all_strategies_no_req_pi = StrategyPack(
        eq_strats=[all_point_placements, point_separation,
                   partial(row_placements, equivalence_only=True),
                   partial(col_placements, equivalence_only=True),
                   partial(point_isolations, equivalence_only=True)],
         ver_strats=[subset_verified, globally_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[partial(components, point_interleaving=True,
                                unions=True)],
                       [all_cell_insertions,
                        partial(row_placements, ignore_equivalence=True),
                        partial(col_placements, ignore_equivalence=True),
                        partial(point_isolations, ignore_equivalence=True)]],
        name="all_strategies_no_req_pi")

all_strategies_no_req_no_eqv_pi = StrategyPack(
        eq_strats=[],
         ver_strats=[subset_verified, globally_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[partial(components, point_interleaving=True,
                                unions=True)],
                       [all_cell_insertions, all_point_placements,
                        point_separation, row_placements, col_placements,
                        point_isolations]],
        name="all_strategies_no_req_no_eqv_pi")

point_sep_and_iso_no_unions_pi = StrategyPack(
        eq_strats=[point_separation],
        ver_strats=[subset_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, point_interleaving=True)],
                      [all_cell_insertions, point_isolations]],
        name="point_sep_and_iso_no_unions_pi")

point_sep_equiv_iso_no_unions_pi = StrategyPack(
        eq_strats=[point_separation,
                   partial(point_isolations, equivalence_only=True)],
        ver_strats=[subset_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, point_interleaving=True)],
                      [all_cell_insertions,
                       partial(point_isolations, ignore_equivalence=True)]],
        name="point_sep_equiv_iso_no_unions_pi")

################################################################################
### WE SHOULD CONSIDER RUNNING POINT SEP AND ISO WITHOUT UNIONS OF COMPONENTS ##
################################################################################
################################################################################
################################################################################
########################## interleaving strategy packs #########################
################################################################################

# SYMMETRY FLAG TURNED TO TRUE!!!!!!!

# QUEUE INTO NORMAL

point_placement_i = StrategyPack(
         eq_strats=[all_point_placements],
         ver_strats=[subset_verified, globally_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[partial(components, interleaving=True)],
                       [all_cell_insertions]],
         name="point_placement_i")

row_column_placements_i = StrategyPack(
        eq_strats=[],
        ver_strats=[subset_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, interleaving=True)],
                      [all_cell_insertions, row_placements,  col_placements]],
        name="row_column_placements_i")

row_column_eqv_placements_i = StrategyPack(
        eq_strats=[partial(row_placements, equivalence_only=True),
                   partial(col_placements, equivalence_only=True)],
        ver_strats=[subset_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, interleaving=True)],
                      [all_cell_insertions,
                       partial(row_placements, ignore_equivalence=True),
                       partial(col_placements, ignore_equivalence=True)]],
        name="row_column_eqv_placements_i")

point_sep_and_iso_i = StrategyPack(
        eq_strats=[point_separation],
        ver_strats=[subset_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True,
                               interleaving=True, workable=False)],
                      [all_cell_insertions, point_isolations]],
        name="point_sep_and_iso_i")

point_sep_equiv_iso_i = StrategyPack(
        eq_strats=[point_separation,
                   partial(point_isolations, equivalence_only=True)],
        ver_strats=[subset_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True,
                               workable=False, interleaving=True)],
                      [all_cell_insertions,
                       partial(point_isolations, ignore_equivalence=True)]],
        name="point_sep_equiv_iso_i")

root_requirement_placements_3_i = StrategyPack(
        eq_strats=[],
        ver_strats=[subset_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, interleaving=True)],
                      [partial(root_requirement_insertions, maxreqlen=3),
                       forced_binary_pattern],
                      [all_cell_insertions, row_placements,  col_placements]],
        name="root_requirement_placements_3_i")

root_requirement_placements_4_i = StrategyPack(
        eq_strats=[],
        ver_strats=[subset_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, interleaving=True)],
                      [partial(root_requirement_insertions, maxreqlen=4),
                       forced_binary_pattern],
                      [all_cell_insertions, row_placements,  col_placements]],
        name="root_requirement_placements_4_i")

all_strategies_no_req_i = StrategyPack(
        eq_strats=[all_point_placements, point_separation,
                   partial(row_placements, equivalence_only=True),
                   partial(col_placements, equivalence_only=True),
                   partial(point_isolations, equivalence_only=True)],
         ver_strats=[subset_verified, globally_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[partial(components, interleaving=True,
                                unions=True)],
                       [all_cell_insertions,
                        partial(row_placements, ignore_equivalence=True),
                        partial(col_placements, ignore_equivalence=True),
                        partial(point_isolations, ignore_equivalence=True)]],
        name="all_strategies_no_req_i")

all_strategies_no_req_no_eqv_i = StrategyPack(
        eq_strats=[],
         ver_strats=[subset_verified, globally_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[partial(components, interleaving=True,
                                unions=True)],
                       [all_cell_insertions, all_point_placements,
                        point_separation, row_placements, col_placements,
                        point_isolations]],
        name="all_strategies_no_req_no_eqv_i")

point_sep_and_iso_no_unions_i = StrategyPack(
        eq_strats=[point_separation],
        ver_strats=[subset_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, interleaving=True)],
                      [all_cell_insertions, point_isolations]],
        name="point_sep_and_iso_no_unions_i")

point_sep_equiv_iso_no_unions_i = StrategyPack(
        eq_strats=[point_separation,
                   partial(point_isolations, equivalence_only=True)],
        ver_strats=[subset_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, interleaving=True)],
                      [all_cell_insertions,
                       partial(point_isolations, ignore_equivalence=True)]],
        name="point_sep_equiv_iso_no_unions_i")

mimic_old_atrap = StrategyPack(
        eq_strats=[partial(row_placements, equivalence_only=True),
                   partial(col_placements, equivalence_only=True)],
        ver_strats=[subset_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, interleaving=True, unions=True, workable=False)],
                      [all_cell_insertions,
                       partial(row_placements, ignore_equivalence=True),
                       partial(col_placements, ignore_equivalence=True)]],
        name="mimic_old_atrap")

############################### Miner verified run Jan 12
################################################################################

# SYMMETRY FLAG TURNED TO FALSE!!!!!!!

# QUEUE INTO omnip

# Time limit: 10 minutes

point_placement_miner = StrategyPack(
         eq_strats=[all_point_placements],
         ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[components],
                       [all_cell_insertions]],
         name="point_placement_miner")

row_column_placements_miner = StrategyPack(
        eq_strats=[],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [all_cell_insertions, row_placements,  col_placements]],
        name="row_column_placements_miner")

row_column_eqv_placements_miner = StrategyPack(
        eq_strats=[partial(row_placements, equivalence_only=True),
                   partial(col_placements, equivalence_only=True)],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [all_cell_insertions,
                       partial(row_placements, ignore_equivalence=True),
                       partial(col_placements, ignore_equivalence=True)]],
        name="row_column_eqv_placements_miner")

point_sep_and_iso_miner = StrategyPack(
        eq_strats=[point_separation],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True, workable=False)],
                      [all_cell_insertions, point_isolations]],
        name="point_sep_and_iso_miner")

point_sep_equiv_iso_miner = StrategyPack(
        eq_strats=[point_separation,
                   partial(point_isolations, equivalence_only=True)],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True, workable=False)],
                      [all_cell_insertions,
                       partial(point_isolations, ignore_equivalence=True)]],
        name="point_sep_equiv_iso_miner")

root_requirement_placements_3_point_placements_miner = StrategyPack(
        eq_strats=[all_point_placements],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [partial(root_requirement_insertions, maxreqlen=3),
                       forced_binary_pattern],
                      [all_cell_insertions]],
        name="root_requirement_placements_3_point_placements_miner")

root_requirement_placements_4_point_placements_miner = StrategyPack(
        eq_strats=[all_point_placements],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [partial(root_requirement_insertions, maxreqlen=4),
                       forced_binary_pattern],
                      [all_cell_insertions]],
        name="root_requirement_placements_4_point_placements_miner")

forced_patterns_3_with_point_placements_miner = StrategyPack(
        eq_strats=[all_point_placements],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True)],
                      [partial(all_requirement_insertions, maxreqlen=3),
                       all_cell_insertions, forced_binary_pattern]],
        name="forced_patterns_3_with_point_placements_miner")

forced_patterns_3_with_row_column_placements_miner = StrategyPack(
        eq_strats=[],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True)],
                      [partial(all_requirement_insertions, maxreqlen=3),
                       all_cell_insertions, row_placements, col_placements,
                       forced_binary_pattern]],
        name="forced_patterns_3_with_row_column_placements_miner")

forced_patterns_4_with_point_placements = StrategyPack(
        eq_strats=[all_point_placements],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True)],
                      [partial(all_requirement_insertions, maxreqlen=4),
                       all_cell_insertions, forced_binary_pattern]],
        name="forced_patterns_4_with_point_placements_miner")

forced_patterns_4_with_row_column_placements_miner = StrategyPack(
        eq_strats=[],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True)],
                      [partial(all_requirement_insertions, maxreqlen=4),
                       all_cell_insertions, row_placements, col_placements,
                       forced_binary_pattern]],
        name="forced_patterns_4_with_row_column_placements_miner")

all_strategies_no_req_miner = StrategyPack(
        eq_strats=[all_point_placements, point_separation,
                   partial(row_placements, equivalence_only=True),
                   partial(col_placements, equivalence_only=True),
                   partial(point_isolations, equivalence_only=True)],
         ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[partial(components, unions=True)],
                       [all_cell_insertions,
                        partial(row_placements, ignore_equivalence=True),
                        partial(col_placements, ignore_equivalence=True),
                        partial(point_isolations, ignore_equivalence=True)]],
        name="all_strategies_no_req_miner")

all_strategies_no_req_no_eqv_miner = StrategyPack(
        eq_strats=[],
         ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[partial(components, unions=True)],
                       [all_cell_insertions, all_point_placements,
                        point_separation, row_placements, col_placements,
                        point_isolations]],
        name="all_strategies_no_req_no_eqv_miner")

point_sep_and_iso_no_unions_miner = StrategyPack(
        eq_strats=[point_separation],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [all_cell_insertions, point_isolations]],
        name="point_sep_and_iso_no_unions_miner")

point_sep_equiv_iso_no_unions_miner = StrategyPack(
        eq_strats=[point_separation,
                   partial(point_isolations, equivalence_only=True)],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [all_cell_insertions,
                       partial(point_isolations, ignore_equivalence=True)]],
        name="point_sep_equiv_iso_no_unions_miner")

mimic_old_atrap_miner = StrategyPack(
        eq_strats=[partial(row_placements, equivalence_only=True),
                   partial(col_placements, equivalence_only=True)],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True, workable=False)],
                      [all_cell_insertions,
                       partial(row_placements, ignore_equivalence=True),
                       partial(col_placements, ignore_equivalence=True)]],
        name="mimic_old_atrap_miner")

############################### Fusion run Jan 12
################################################################################

# SYMMETRY FLAG TURNED TO FALSE!!!!!!!

# QUEUE INTO omnip

# FORWARD EQUIVALENCE NOW ON!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Time limit: 2 weeks

point_placement_fusion = StrategyPack(
         eq_strats=[fusion, all_point_placements],
         ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[components],
                       [all_cell_insertions]],
         name="point_placement_fusion")

row_column_placements_fusion = StrategyPack(
        eq_strats=[fusion],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [all_cell_insertions, row_placements,  col_placements]],
        name="row_column_placements_fusion")

row_column_eqv_placements_fusion = StrategyPack(
        eq_strats=[fusion, partial(row_placements, equivalence_only=True),
                   partial(col_placements, equivalence_only=True)],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [all_cell_insertions,
                       partial(row_placements, ignore_equivalence=True),
                       partial(col_placements, ignore_equivalence=True)]],
        name="row_column_eqv_placements_fusion")

point_sep_and_iso_fusion = StrategyPack(
        eq_strats=[fusion, point_separation],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True, workable=False)],
                      [all_cell_insertions, point_isolations]],
        name="point_sep_and_iso_fusion")

point_sep_equiv_iso_fusion = StrategyPack(
        eq_strats=[fusion, point_separation,
                   partial(point_isolations, equivalence_only=True)],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True, workable=False)],
                      [all_cell_insertions,
                       partial(point_isolations, ignore_equivalence=True)]],
        name="point_sep_equiv_iso_fusion")

root_requirement_placements_3_point_placements_fusion = StrategyPack(
        eq_strats=[fusion, all_point_placements],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [partial(root_requirement_insertions, maxreqlen=3),
                       forced_binary_pattern],
                      [all_cell_insertions]],
        name="root_requirement_placements_3_point_placements_fusion")

root_requirement_placements_4_point_placements_fusion = StrategyPack(
        eq_strats=[fusion, all_point_placements],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [partial(root_requirement_insertions, maxreqlen=4),
                       forced_binary_pattern],
                      [all_cell_insertions]],
        name="root_requirement_placements_4_point_placements_fusion")

all_strategies_no_req_fusion = StrategyPack(
        eq_strats=[fusion, all_point_placements, point_separation,
                   partial(row_placements, equivalence_only=True),
                   partial(col_placements, equivalence_only=True),
                   partial(point_isolations, equivalence_only=True)],
         ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[partial(components, unions=True)],
                       [all_cell_insertions,
                        partial(row_placements, ignore_equivalence=True),
                        partial(col_placements, ignore_equivalence=True),
                        partial(point_isolations, ignore_equivalence=True)]],
        name="all_strategies_no_req_fusion")

all_strategies_no_req_no_eqv_fusion = StrategyPack(
        eq_strats=[fusion],
         ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[partial(components, unions=True)],
                       [all_cell_insertions, all_point_placements,
                        point_separation, row_placements, col_placements,
                        point_isolations]],
        name="all_strategies_no_req_no_eqv_fusion")

point_sep_and_iso_no_unions_fusion = StrategyPack(
        eq_strats=[fusion, point_separation],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [all_cell_insertions, point_isolations]],
        name="point_sep_and_iso_no_unions_fusion")

point_sep_equiv_iso_no_unions_fusion = StrategyPack(
        eq_strats=[fusion, point_separation,
                   partial(point_isolations, equivalence_only=True)],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [all_cell_insertions,
                       partial(point_isolations, ignore_equivalence=True)]],
        name="point_sep_equiv_iso_no_unions_fusion")

mimic_old_atrap_fusion = StrategyPack(
        eq_strats=[fusion, partial(row_placements, equivalence_only=True),
                   partial(col_placements, equivalence_only=True)],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True, workable=False)],
                      [all_cell_insertions,
                       partial(row_placements, ignore_equivalence=True),
                       partial(col_placements, ignore_equivalence=True)]],
        name="mimic_old_atrap_fusion")


############################### Deflation run Jan 17
################################################################################

point_placement_deflation = StrategyPack(
         eq_strats=[all_point_placements, deflation],
         ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[components],
                       [all_cell_insertions]],
         name="point_placement_deflation")

row_column_placements_deflation = StrategyPack(
        eq_strats=[deflation],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [all_cell_insertions, row_placements,  col_placements]],
        name="row_column_placements_deflation")

row_column_eqv_placements_deflation = StrategyPack(
        eq_strats=[partial(row_placements, equivalence_only=True),
                   partial(col_placements, equivalence_only=True),
                   deflation],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [all_cell_insertions,
                       partial(row_placements, ignore_equivalence=True),
                       partial(col_placements, ignore_equivalence=True)]],
        name="row_column_eqv_placements_deflation")

point_sep_and_iso_deflation = StrategyPack(
        eq_strats=[point_separation, deflation],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True, workable=False)],
                      [all_cell_insertions, point_isolations]],
        name="point_sep_and_iso_deflation")

point_sep_equiv_iso_deflation = StrategyPack(
        eq_strats=[point_separation,
                   partial(point_isolations, equivalence_only=True),
                   deflation],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True, workable=False)],
                      [all_cell_insertions,
                       partial(point_isolations, ignore_equivalence=True)]],
        name="point_sep_equiv_iso_deflation")

root_requirement_placements_3_point_placements_deflation = StrategyPack(
        eq_strats=[all_point_placements, deflation],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [partial(root_requirement_insertions, maxreqlen=3),
                       forced_binary_pattern],
                      [all_cell_insertions]],
        name="root_requirement_placements_3_point_placements_deflation")

root_requirement_placements_4_point_placements_deflation = StrategyPack(
        eq_strats=[all_point_placements, deflation],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [partial(root_requirement_insertions, maxreqlen=4),
                       forced_binary_pattern],
                      [all_cell_insertions]],
        name="root_requirement_placements_4_point_placements_deflation")

forced_patterns_3_with_point_placements_deflation = StrategyPack(
        eq_strats=[all_point_placements, deflation],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True)],
                      [partial(all_requirement_insertions, maxreqlen=3),
                       all_cell_insertions, forced_binary_pattern]],
        name="forced_patterns_3_with_point_placements_deflation")

forced_patterns_3_with_row_column_placements_deflation = StrategyPack(
        eq_strats=[deflation],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True)],
                      [partial(all_requirement_insertions, maxreqlen=3),
                       all_cell_insertions, row_placements, col_placements,
                       forced_binary_pattern]],
        name="forced_patterns_3_with_row_column_placements_deflation")

forced_patterns_4_with_point_placements = StrategyPack(
        eq_strats=[all_point_placements, deflation],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True)],
                      [partial(all_requirement_insertions, maxreqlen=4),
                       all_cell_insertions, forced_binary_pattern]],
        name="forced_patterns_4_with_point_placements_deflation")

forced_patterns_4_with_row_column_placements_deflation = StrategyPack(
        eq_strats=[deflation],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True)],
                      [partial(all_requirement_insertions, maxreqlen=4),
                       all_cell_insertions, row_placements, col_placements,
                       forced_binary_pattern]],
        name="forced_patterns_4_with_row_column_placements_deflation")

all_strategies_no_req_deflation = StrategyPack(
        eq_strats=[all_point_placements, point_separation,
                   partial(row_placements, equivalence_only=True),
                   partial(col_placements, equivalence_only=True),
                   partial(point_isolations, equivalence_only=True),
                   deflation],
         ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[partial(components, unions=True)],
                       [all_cell_insertions,
                        partial(row_placements, ignore_equivalence=True),
                        partial(col_placements, ignore_equivalence=True),
                        partial(point_isolations, ignore_equivalence=True)]],
        name="all_strategies_no_req_deflation")

all_strategies_no_req_no_eqv_deflation = StrategyPack(
        eq_strats=[deflation],
         ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[partial(components, unions=True)],
                       [all_cell_insertions, all_point_placements,
                        point_separation, row_placements, col_placements,
                        point_isolations]],
        name="all_strategies_no_req_no_eqv_deflation")

point_sep_and_iso_no_unions_deflation = StrategyPack(
        eq_strats=[point_separation, deflation],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [all_cell_insertions, point_isolations]],
        name="point_sep_and_iso_no_unions_deflation")

point_sep_equiv_iso_no_unions_deflation = StrategyPack(
        eq_strats=[point_separation,
                   partial(point_isolations, equivalence_only=True),
                   deflation],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [all_cell_insertions,
                       partial(point_isolations, ignore_equivalence=True)]],
        name="point_sep_equiv_iso_no_unions_deflation")

mimic_old_atrap_deflation = StrategyPack(
        eq_strats=[partial(row_placements, equivalence_only=True),
                   partial(col_placements, equivalence_only=True),
                   deflation],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True, workable=False)],
                      [all_cell_insertions,
                       partial(row_placements, ignore_equivalence=True),
                       partial(col_placements, ignore_equivalence=True)]],
        name="mimic_old_atrap_deflation")

############################### Deflation+fusion run Jan 20ish
################################################################################

point_placement_defusion = StrategyPack(
         eq_strats=[all_point_placements, deflation, fusion],
         ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[components],
                       [all_cell_insertions]],
         name="point_placement_defusion")

row_column_placements_defusion = StrategyPack(
        eq_strats=[deflation, fusion],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [all_cell_insertions, row_placements,  col_placements]],
        name="row_column_placements_defusion")

row_column_eqv_placements_defusion = StrategyPack(
        eq_strats=[partial(row_placements, equivalence_only=True),
                   partial(col_placements, equivalence_only=True),
                   deflation, fusion],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [all_cell_insertions,
                       partial(row_placements, ignore_equivalence=True),
                       partial(col_placements, ignore_equivalence=True)]],
        name="row_column_eqv_placements_defusion")

point_sep_and_iso_defusion = StrategyPack(
        eq_strats=[point_separation, deflation, fusion],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True, workable=False)],
                      [all_cell_insertions, point_isolations]],
        name="point_sep_and_iso_defusion")

point_sep_equiv_iso_defusion = StrategyPack(
        eq_strats=[point_separation,
                   partial(point_isolations, equivalence_only=True),
                   deflation, fusion],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True, workable=False)],
                      [all_cell_insertions,
                       partial(point_isolations, ignore_equivalence=True)]],
        name="point_sep_equiv_iso_defusion")

root_requirement_placements_3_point_placements_defusion = StrategyPack(
        eq_strats=[all_point_placements, deflation, fusion],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [partial(root_requirement_insertions, maxreqlen=3),
                       forced_binary_pattern],
                      [all_cell_insertions]],
        name="root_requirement_placements_3_point_placements_defusion")

root_requirement_placements_4_point_placements_defusion = StrategyPack(
        eq_strats=[all_point_placements, deflation, fusion],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [partial(root_requirement_insertions, maxreqlen=4),
                       forced_binary_pattern],
                      [all_cell_insertions]],
        name="root_requirement_placements_4_point_placements_defusion")

all_strategies_no_req_defusion = StrategyPack(
        eq_strats=[all_point_placements, point_separation,
                   partial(row_placements, equivalence_only=True),
                   partial(col_placements, equivalence_only=True),
                   partial(point_isolations, equivalence_only=True),
                   deflation, fusion],
         ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[partial(components, unions=True)],
                       [all_cell_insertions,
                        partial(row_placements, ignore_equivalence=True),
                        partial(col_placements, ignore_equivalence=True),
                        partial(point_isolations, ignore_equivalence=True)]],
        name="all_strategies_no_req_defusion")

all_strategies_no_req_no_eqv_defusion = StrategyPack(
        eq_strats=[deflation, fusion],
         ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[partial(components, unions=True)],
                       [all_cell_insertions, all_point_placements,
                        point_separation, row_placements, col_placements,
                        point_isolations]],
        name="all_strategies_no_req_no_eqv_defusion")

point_sep_and_iso_no_unions_defusion = StrategyPack(
        eq_strats=[point_separation, deflation, fusion],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [all_cell_insertions, point_isolations]],
        name="point_sep_and_iso_no_unions_defusion")

point_sep_equiv_iso_no_unions_defusion = StrategyPack(
        eq_strats=[point_separation,
                   partial(point_isolations, equivalence_only=True),
                   deflation, fusion],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [all_cell_insertions,
                       partial(point_isolations, ignore_equivalence=True)]],
        name="point_sep_equiv_iso_no_unions_defusion")

mimic_old_atrap_defusion = StrategyPack(
        eq_strats=[partial(row_placements, equivalence_only=True),
                   partial(col_placements, equivalence_only=True),
                   deflation, fusion],
        ver_strats=[subset_verified, globally_verified, database_verified, miner_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True, workable=False)],
                      [all_cell_insertions,
                       partial(row_placements, ignore_equivalence=True),
                       partial(col_placements, ignore_equivalence=True)]],
        name="mimic_old_atrap_defusion")

################################################################################
### WE SHOULD CONSIDER RUNNING POINT SEP AND ISO WITHOUT UNIONS OF COMPONENTS ##
################################################################################

forced_patterns_2_basic = StrategyPack(
        eq_strats=[],
        ver_strats=[subset_verified, database_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[components],
                      [partial(all_requirement_insertions, maxreqlen=2),
                       all_cell_insertions, forced_binary_pattern]],
        name="forced_patterns_2_basic")

# other stuff

forced_patterns_3_with_row_column_placements_pi = StrategyPack(
        eq_strats=[],
        ver_strats=[subset_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True,
                               point_interleaving=True)],
                      [partial(all_requirement_insertions, maxreqlen=3),
                       all_cell_insertions, row_placements, col_placements,
                       forced_binary_pattern]],
        name="forced_patterns_3_with_row_column_placements_pi")

forced_patterns_4_with_row_column_placements_pi = StrategyPack(
        eq_strats=[],
        ver_strats=[subset_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True,
                               point_interleaving=True)],
                      [partial(all_requirement_insertions, maxreqlen=4),
                       all_cell_insertions, row_placements, col_placements,
                       forced_binary_pattern]],
        name="forced_patterns_4_with_row_column_placements_pi")

forced_patterns_3_with_point_placements_pi = StrategyPack(
        eq_strats=[all_point_placements],
        ver_strats=[subset_verified, database_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True,
                               point_interleaving=True)],
                      [partial(all_requirement_insertions, maxreqlen=3),
                       all_cell_insertions, forced_binary_pattern]],
        name="forced_patterns_3_with_point_placements_pi")

forced_patterns_4_with_point_placements_pi = StrategyPack(
        eq_strats=[all_point_placements],
        ver_strats=[subset_verified, database_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, unions=True,
                               point_interleaving=True)],
                      [partial(all_requirement_insertions, maxreqlen=4),
                       all_cell_insertions, forced_binary_pattern]],
        name="forced_patterns_4_with_point_placements_pi")

point_placement_fusion = StrategyPack(
         eq_strats=[all_point_placements, fusion],
         ver_strats=[subset_verified],
         inf_strats=[empty_cell_inferral, row_and_column_separation],
         other_strats=[[components],
                       [all_cell_insertions]],
         name="point_placement_fusion")

point_sep_equiv_iso_fusion = StrategyPack(
        eq_strats=[point_separation, fusion,
                   partial(point_isolations, equivalence_only=True)],
        ver_strats=[subset_verified, globally_verified],
        inf_strats=[empty_cell_inferral, row_and_column_separation],
        other_strats=[[partial(components, interleaving=False)],
                      [all_cell_insertions,
                       partial(point_isolations, ignore_equivalence=True)]],
        name="point_sep_equiv_iso_fusion")

# point_placement_deflation_fusion = StrategyPack(
#          eq_strats=[all_point_placements, deflation, fusion],
#          ver_strats=[subset_verified, miner_verified],
#          inf_strats=[empty_cell_inferral, row_and_column_separation],
#          other_strats=[[components],
#                        [all_cell_insertions]],
#          name="point_placement_deflation")

#
# point_placement_one_cell_inferral = StrategyPack(
#          eq_strats=[all_point_placements],
#          ver_strats=[subset_verified],
#          inf_strats=[empty_cell_inferral],
#          other_strats=[[components], [all_cell_insertions]],
#          name="point_placement")
#
# point_placement_no_infer = StrategyPack(
#          eq_strats=[all_point_placements],
#          ver_strats=[subset_verified],
#          inf_strats=[empty_cell_inferral],
#          other_strats=[[components], [all_cell_insertions]],
#          name="point_placement_no_infer")
#
# row_placements_only = StrategyPack(
#          eq_strats=[],
#          ver_strats=[subset_verified],
#          inf_strats=[empty_cell_inferral, row_and_column_separation],
#          other_strats=[[components],[all_cell_insertions, row_placements]],
#          name="row_placements")
#
# col_placements_only = StrategyPack(
#          eq_strats=[],
#          ver_strats=[subset_verified],
#          inf_strats=[empty_cell_inferral, row_and_column_separation],
#          other_strats=[[components], [all_cell_insertions, col_placements]],
#          name="col_placements")
#
# row_and_column_placements = StrategyPack(
#          eq_strats=[],
#          ver_strats=[subset_verified],
#          inf_strats=[empty_cell_inferral, row_and_column_separation],
#          other_strats=[[components],
#                        [all_cell_insertions, row_placements, col_placements]],
#          name="row_and_column_placements")
#
# row_and_column_placements_and_database = StrategyPack(
#          eq_strats=[],
#          ver_strats=[subset_verified, database_verified],
#          inf_strats=[empty_cell_inferral, row_and_column_separation],
#          other_strats=[[components],
#                        [all_cell_insertions, row_placements, col_placements]],
#          name="row_and_column_placements_and_database")
#
# point_separation_and_row_col_placements = StrategyPack(
#          eq_strats=[point_separation],
#          ver_strats=[subset_verified],
#          inf_strats=[empty_cell_inferral, row_and_column_separation],
#          other_strats=[[components],
#                        [all_cell_insertions,
#                         partial(row_placements, all_positive_in_row=False),
#                         partial(col_placements, all_positive_in_col=False)]],
#          name="row_and_column_placements")
#
# binary_force_only = StrategyPack(
#     eq_strats=[forced_binary_pattern],
#     ver_strats=[subset_verified],
#     inf_strats=[empty_cell_inferral, row_and_column_separation],
#     other_strats=[[partial(components, unions=True)],
#                   [all_cell_insertions],
#                   [partial(all_requirement_insertions, maxreqlength=4)],
#                   ],
#     name="binary_force w/ row-col separation and cell insertions")
#
# point_separation_and_isolation = StrategyPack(
#          eq_strats=[point_separation],
#          ver_strats=[subset_verified],
#          inf_strats=[empty_cell_inferral, row_and_column_separation],
#          other_strats=[[partial(components, workable=False, unions=True)],
#                        [all_cell_insertions, point_isolations]],
#          name="point_separation_and_isolation")
