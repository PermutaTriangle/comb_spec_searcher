from atrapv2.strategies import *
from comb_spec_searcher import StrategyPack

row_and_column_placements_at_once = StrategyPack(name="row_and_column_placements_at_once",
     eq_strats=[all_equivalent_row_placements, all_equivalent_column_placements],
     ver_strats=[subset_verified],
     inf_strats=[empty_cell_inferral, row_and_column_separation, subclass_inferral],
     other_strats=[[components, reversibly_deletable_cells, all_cell_insertions, all_row_placements, all_column_placements]])

row_and_column_insertion_and_splittings_batch_first = StrategyPack(name="row_and_column_placements_batch_first",
     eq_strats=[all_equivalent_point_isolations],
     ver_strats=[subset_verified],
     inf_strats=[empty_cell_inferral, row_and_column_separation, subclass_inferral],
     other_strats=[[all_row_and_column_insertions, all_point_isolations],[splittings]])

row_and_column_insertion_and_splittings_at_once = StrategyPack( name="row_and_column_insertion_and_splittings_at_once",
    eq_strats =  [all_equivalent_point_isolations],
    inf_strats = [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    ver_strats = [subset_verified],
    other_strats = [[splittings, all_row_and_column_insertions, all_point_isolations]])


# all mostly for testing purposes
all_strategies = StrategyPack(name="all_strategies",
                              eq_strats=[all_point_placements,
                                         point_separation,
                                         all_equivalent_point_isolations],
                              inf_strats=[empty_cell_inferral,
                                          row_and_column_separation,
                                          subclass_inferral],
                              ver_strats=[subset_verified],
                              other_strats=[[all_cell_insertions,
                                             all_point_isolations,
                                             all_row_and_column_insertions,
                                             all_row_placements,
                                             all_column_placements,
                                             binary_pattern,
                                             binary_pattern_classical_class,
                                             classical_binary_pattern,
                                             extreme_point_boundaries],
                                            [reversibly_deletable_cells,
                                             components,
                                             splittings]])

row_and_column_placements = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

minimum_row_placements = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

minimum_row_placements_and_splittings = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

minimum_row_no_rec = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

minimum_row_placements_and_point_separation = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

minimum_row_placements_and_splittings_and_point_separation = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_placements = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_placements_and_splittings = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_placements_no_rec = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_placements_and_point_separation = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_placements_and_splittings_and_point_separation = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

left_column_placements = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

left_column_placements_and_splittings = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

left_column_placements_no_rec = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

left_column_placements_and_point_separation = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

left_column_placements_and_splittings_and_point_separation = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

column_placements = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

column_placements_and_splittings = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

column_placements_no_rec = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

column_placements_and_point_separation = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

column_placements_and_splittings_and_point_separation = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_placements = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_placements_and_splittings = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_placements_no_rec = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_placements_and_point_separation = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_placements_and_splittings_and_point_separation = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

point_placement = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

point_placement_and_splittings = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

point_placement_and_point_separation = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

point_placement_and_splittings_and_point_separation = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

point_separation_and_isolation = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

point_separation_and_isolation_and_splittings = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

point_placement_and_all_lrm_and_rlm_placements = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

point_placement_and_all_lrm_and_rlm_placements_and_splittings = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_placements_and_all_lrm_and_rlm_placements = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_placements_and_all_lrm_and_rlm_placements_and_splittings = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

point_placement_and_all_321_boundaries = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_321_boundaries],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

point_placement_and_all_321_boundaries_and_splittings = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_321_boundaries],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_placements_and_all_321_boundaries = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_321_boundaries],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_placements_and_all_321_boundaries_and_splittings = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_321_boundaries],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

finite = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

mimic_regular_insertion_encoding = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, minimum_insertion_encoding_row_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [],
    "recursive_strategies": [reversibly_deletable_points],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

mimic_regular_insertion_encoding_flip = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, leftmost_insertion_encoding_column_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [],
    "recursive_strategies": [reversibly_deletable_points],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

mimic_regular_insertion_encoding_but_better = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, minimum_insertion_encoding_row_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

mimic_regular_insertion_encoding_flip_but_better = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, leftmost_insertion_encoding_column_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

mimic_regular_insertion_encoding_but_better_from_all_angles = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, insertion_encoding_row_placements, insertion_encoding_column_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

mimic_Zeilberger_enumeration_schemes = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral],
    "recursive_strategies": [reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

left_to_right_maxima_123_and_point_placements = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, left_to_right_maxima123],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

left_to_right_maxima_1234_and_point_placements = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, left_to_right_maxima1234],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

left_to_right_maxima_123_and_row_column_placements = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, left_to_right_maxima123, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

left_to_right_maxima_1234_and_row_column_placements = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, left_to_right_maxima1234, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

point_separation_and_isolation_with_left_to_right_maxima1234 = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, left_to_right_maxima1234, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_insertion = StrategyPack(old_pack={
    "batch_strategies": [all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_insertion_and_cell_insertion = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_insertion_and_cell_insertion_and_point_separation = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_insertion_and_splittings = StrategyPack(old_pack={
    "batch_strategies": [all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_insertion_and_cell_insertion_and_splittings = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_insertion_and_cell_insertion_and_point_separation_and_splittings = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

jays_special = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_point_placements, all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

jays_special_no_rec = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_point_placements, all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

extreme_points = StrategyPack(old_pack={
    "batch_strategies": [extreme_point_boundaries, all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_point_placements, all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

# --------------------------------------------------------------------------
# Below is an exact copy of the strategy packs at the top, but with symmetries
# --------------------------------------------------------------------------

all_strategies_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_point_isolations],
    "equivalence_strategies": [all_point_placements, point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

minimum_row_placements_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

minimum_row_placements_and_splittings_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

minimum_row_no_rec_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

minimum_row_placements_and_point_separation_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

minimum_row_placements_and_splittings_and_point_separation_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_placements_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_placements_and_splittings_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_placements_no_rec_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_placements_and_point_separation_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_placements_and_splittings_and_point_separation_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

left_column_placements_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

left_column_placements_and_splittings_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

left_column_placements_no_rec_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

left_column_placements_and_point_separation_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

left_column_placements_and_splittings_and_point_separation_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

column_placements_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

column_placements_and_splittings_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

column_placements_no_rec_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

column_placements_and_point_separation_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

column_placements_and_splittings_and_point_separation_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_placements_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_placements_and_splittings_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_placements_no_rec_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_placements_and_point_separation_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_placements_and_splittings_and_point_separation_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

point_placement_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

point_placement_and_splittings_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

point_placement_and_point_separation_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

point_placement_and_splittings_and_point_separation_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

point_separation_and_isolation_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

point_separation_and_isolation_and_splittings_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

point_placement_and_all_lrm_and_rlm_placements_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

point_placement_and_all_lrm_and_rlm_placements_and_splittings_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_placements_and_all_lrm_and_rlm_placements_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_placements_and_all_lrm_and_rlm_placements_and_splittings_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

point_placement_and_all_321_boundaries_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_321_boundaries],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

point_placement_and_all_321_boundaries_and_splittings_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_321_boundaries],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_placements_and_all_321_boundaries_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_321_boundaries],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_placements_and_all_321_boundaries_and_splittings_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_321_boundaries],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

finite_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

mimic_regular_insertion_encoding_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, minimum_insertion_encoding_row_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [],
    "recursive_strategies": [reversibly_deletable_points],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

mimic_regular_insertion_encoding_flip_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, leftmost_insertion_encoding_column_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [],
    "recursive_strategies": [reversibly_deletable_points],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

mimic_regular_insertion_encoding_but_better_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, minimum_insertion_encoding_row_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

mimic_regular_insertion_encoding_flip_but_better_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, leftmost_insertion_encoding_column_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

mimic_regular_insertion_encoding_but_better_from_all_angles_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, insertion_encoding_row_placements, insertion_encoding_column_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

mimic_Zeilberger_enumeration_schemes_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral],
    "recursive_strategies": [reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

left_to_right_maxima_123_and_point_placements_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, left_to_right_maxima123],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

left_to_right_maxima_1234_and_point_placements_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, left_to_right_maxima1234],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

left_to_right_maxima_123_and_row_column_placements_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, left_to_right_maxima123, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

left_to_right_maxima_1234_and_row_column_placements_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, left_to_right_maxima1234, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

point_separation_and_isolation_with_left_to_right_maxima1234_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, left_to_right_maxima1234, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_insertion_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_insertion_and_cell_insertion_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_insertion_and_cell_insertion_and_point_separation_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_insertion_and_splittings_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_insertion_and_cell_insertion_and_splittings_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

row_and_column_insertion_and_cell_insertion_and_point_separation_and_splittings_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

jays_special_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_point_placements, all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

jays_special_no_rec_w_symm = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_point_placements, all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

extreme_points_w_symm = StrategyPack(old_pack={
    "batch_strategies": [extreme_point_boundaries, all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_point_placements, all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

# --------------------------------------------------------------------------
# Below is an exact copy of the strategy packs at the top, but without interleaving recursions
# --------------------------------------------------------------------------

all_strategies_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_point_isolations],
    "equivalence_strategies": [all_point_placements, point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

minimum_row_placements_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

minimum_row_placements_and_splittings_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

minimum_row_no_rec_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

minimum_row_placements_and_point_separation_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

minimum_row_placements_and_splittings_and_point_separation_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

row_placements_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

row_placements_and_splittings_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

row_placements_no_rec_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

row_placements_and_point_separation_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

row_placements_and_splittings_and_point_separation_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

left_column_placements_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

left_column_placements_and_splittings_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

left_column_placements_no_rec_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

left_column_placements_and_point_separation_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

left_column_placements_and_splittings_and_point_separation_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

column_placements_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

column_placements_and_splittings_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

column_placements_no_rec_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

column_placements_and_point_separation_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

column_placements_and_splittings_and_point_separation_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

row_and_column_placements_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

row_and_column_placements_and_splittings_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

row_and_column_placements_no_rec_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

row_and_column_placements_and_point_separation_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

row_and_column_placements_and_splittings_and_point_separation_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

point_placement_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

point_placement_and_splittings_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

point_placement_and_point_separation_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

point_placement_and_splittings_and_point_separation_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

point_separation_and_isolation_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

point_separation_and_isolation_and_splittings_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

point_placement_and_all_lrm_and_rlm_placements_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

point_placement_and_all_lrm_and_rlm_placements_and_splittings_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

row_and_column_placements_and_all_lrm_and_rlm_placements_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

row_and_column_placements_and_all_lrm_and_rlm_placements_and_splittings_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

point_placement_and_all_321_boundaries_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_321_boundaries],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

point_placement_and_all_321_boundaries_and_splittings_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_321_boundaries],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

row_and_column_placements_and_all_321_boundaries_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_321_boundaries],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

row_and_column_placements_and_all_321_boundaries_and_splittings_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_321_boundaries],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

finite_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

mimic_regular_insertion_encoding_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, minimum_insertion_encoding_row_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [],
    "recursive_strategies": [reversibly_deletable_points],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

mimic_regular_insertion_encoding_flip_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, leftmost_insertion_encoding_column_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [],
    "recursive_strategies": [reversibly_deletable_points],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

mimic_regular_insertion_encoding_but_better_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, minimum_insertion_encoding_row_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

mimic_regular_insertion_encoding_flip_but_better_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, leftmost_insertion_encoding_column_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

mimic_regular_insertion_encoding_but_better_from_all_angles_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, insertion_encoding_row_placements, insertion_encoding_column_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

mimic_Zeilberger_enumeration_schemes_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral],
    "recursive_strategies": [reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

left_to_right_maxima_123_and_point_placements_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, left_to_right_maxima123],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

left_to_right_maxima_1234_and_point_placements_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, left_to_right_maxima1234],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

left_to_right_maxima_123_and_row_column_placements_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, left_to_right_maxima123, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

left_to_right_maxima_1234_and_row_column_placements_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, left_to_right_maxima1234, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

point_separation_and_isolation_with_left_to_right_maxima1234_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, left_to_right_maxima1234, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

row_and_column_insertion_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

row_and_column_insertion_and_cell_insertion_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

row_and_column_insertion_and_cell_insertion_and_point_separation_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

row_and_column_insertion_and_splittings_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

row_and_column_insertion_and_cell_insertion_and_splittings_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

row_and_column_insertion_and_cell_insertion_and_point_separation_and_splittings_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

jays_special_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_point_placements, all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

jays_special_no_rec_non_interl = StrategyPack(old_pack={
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_point_placements, all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

extreme_points_non_interl = StrategyPack(old_pack={
    "batch_strategies": [extreme_point_boundaries, all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_point_placements, all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    })

classical_binary_pattern_placement  = StrategyPack(old_pack={
    "batch_strategies": [classical_binary_pattern, all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

binary_pattern_classical_class_placement  = StrategyPack(old_pack={
    "batch_strategies": [binary_pattern_classical_class, all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })

binary_pattern_placement  = StrategyPack(old_pack={
    "batch_strategies": [binary_pattern, all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    })
