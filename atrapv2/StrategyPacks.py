from atrapv2.strategies import *

all_strategies = {
    "batch_strategies": [all_cell_insertions, all_point_isolations],
    "equivalence_strategies": [all_point_placements, point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

minimum_row_placements = {
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

minimum_row_placements_and_splittings = {
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

minimum_row_no_rec = {
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

minimum_row_placements_and_point_separation = {
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

minimum_row_placements_and_splittings_and_point_separation = {
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_placements = {
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_placements_and_splittings = {
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_placements_no_rec = {
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_placements_and_point_separation = {
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_placements_and_splittings_and_point_separation = {
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

left_column_placements = {
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

left_column_placements_and_splittings = {
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

left_column_placements_no_rec = {
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

left_column_placements_and_point_separation = {
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

left_column_placements_and_splittings_and_point_separation = {
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

column_placements = {
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

column_placements_and_splittings = {
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

column_placements_no_rec = {
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

column_placements_and_point_separation = {
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

column_placements_and_splittings_and_point_separation = {
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_placements = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_placements_and_splittings = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_placements_no_rec = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_placements_and_point_separation = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_placements_and_splittings_and_point_separation = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

point_placement = {
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

point_placement_and_splittings = {
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

point_placement_and_point_separation = {
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

point_placement_and_splittings_and_point_separation = {
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

point_separation_and_isolation = {
    "batch_strategies": [all_cell_insertions, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

point_separation_and_isolation_and_splittings = {
    "batch_strategies": [all_cell_insertions, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

point_placement_and_all_lrm_and_rlm_placements = {
    "batch_strategies": [all_cell_insertions, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

point_placement_and_all_lrm_and_rlm_placements_and_splittings = {
    "batch_strategies": [all_cell_insertions, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_placements_and_all_lrm_and_rlm_placements = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_placements_and_all_lrm_and_rlm_placements_and_splittings = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

point_placement_and_all_321_boundaries = {
    "batch_strategies": [all_cell_insertions, all_321_boundaries],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

point_placement_and_all_321_boundaries_and_splittings = {
    "batch_strategies": [all_cell_insertions, all_321_boundaries],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_placements_and_all_321_boundaries = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_321_boundaries],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_placements_and_all_321_boundaries_and_splittings = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_321_boundaries],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

finite = {
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

mimic_regular_insertion_encoding = {
    "batch_strategies": [all_cell_insertions, minimum_insertion_encoding_row_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [],
    "recursive_strategies": [reversibly_deletable_points],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

mimic_regular_insertion_encoding_flip = {
    "batch_strategies": [all_cell_insertions, leftmost_insertion_encoding_column_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [],
    "recursive_strategies": [reversibly_deletable_points],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

mimic_regular_insertion_encoding_but_better = {
    "batch_strategies": [all_cell_insertions, minimum_insertion_encoding_row_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

mimic_regular_insertion_encoding_flip_but_better = {
    "batch_strategies": [all_cell_insertions, leftmost_insertion_encoding_column_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

mimic_regular_insertion_encoding_but_better_from_all_angles = {
    "batch_strategies": [all_cell_insertions, insertion_encoding_row_placements, insertion_encoding_column_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

mimic_Zeilberger_enumeration_schemes = {
    "batch_strategies": [all_cell_insertions, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral],
    "recursive_strategies": [reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

left_to_right_maxima_123_and_point_placements = {
    "batch_strategies": [all_cell_insertions, left_to_right_maxima123],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

left_to_right_maxima_1234_and_point_placements = {
    "batch_strategies": [all_cell_insertions, left_to_right_maxima1234],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

left_to_right_maxima_123_and_row_column_placements = {
    "batch_strategies": [all_cell_insertions, left_to_right_maxima123, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

left_to_right_maxima_1234_and_row_column_placements = {
    "batch_strategies": [all_cell_insertions, left_to_right_maxima1234, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

point_separation_and_isolation_with_left_to_right_maxima1234 = {
    "batch_strategies": [all_cell_insertions, left_to_right_maxima1234, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_insertion = {
    "batch_strategies": [all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_insertion_and_cell_insertion = {
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_insertion_and_cell_insertion_and_point_separation = {
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_insertion_and_splittings = {
    "batch_strategies": [all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_insertion_and_cell_insertion_and_splittings = {
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_insertion_and_cell_insertion_and_point_separation_and_splittings = {
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

jays_special = {
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_point_placements, all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

jays_special_no_rec = {
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_point_placements, all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

extreme_points = {
    "batch_strategies": [extreme_point_boundaries, all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_point_placements, all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

# --------------------------------------------------------------------------
# Below is an exact copy of the strategy packs at the top, but with symmetries
# --------------------------------------------------------------------------

all_strategies_w_symm = {
    "batch_strategies": [all_cell_insertions, all_point_isolations],
    "equivalence_strategies": [all_point_placements, point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

minimum_row_placements_w_symm = {
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

minimum_row_placements_and_splittings_w_symm = {
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

minimum_row_no_rec_w_symm = {
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

minimum_row_placements_and_point_separation_w_symm = {
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

minimum_row_placements_and_splittings_and_point_separation_w_symm = {
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_placements_w_symm = {
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_placements_and_splittings_w_symm = {
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_placements_no_rec_w_symm = {
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_placements_and_point_separation_w_symm = {
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_placements_and_splittings_and_point_separation_w_symm = {
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

left_column_placements_w_symm = {
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

left_column_placements_and_splittings_w_symm = {
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

left_column_placements_no_rec_w_symm = {
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

left_column_placements_and_point_separation_w_symm = {
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

left_column_placements_and_splittings_and_point_separation_w_symm = {
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

column_placements_w_symm = {
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

column_placements_and_splittings_w_symm = {
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

column_placements_no_rec_w_symm = {
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

column_placements_and_point_separation_w_symm = {
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

column_placements_and_splittings_and_point_separation_w_symm = {
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_placements_w_symm = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_placements_and_splittings_w_symm = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_placements_no_rec_w_symm = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_placements_and_point_separation_w_symm = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_placements_and_splittings_and_point_separation_w_symm = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

point_placement_w_symm = {
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

point_placement_and_splittings_w_symm = {
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

point_placement_and_point_separation_w_symm = {
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

point_placement_and_splittings_and_point_separation_w_symm = {
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

point_separation_and_isolation_w_symm = {
    "batch_strategies": [all_cell_insertions, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

point_separation_and_isolation_and_splittings_w_symm = {
    "batch_strategies": [all_cell_insertions, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

point_placement_and_all_lrm_and_rlm_placements_w_symm = {
    "batch_strategies": [all_cell_insertions, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

point_placement_and_all_lrm_and_rlm_placements_and_splittings_w_symm = {
    "batch_strategies": [all_cell_insertions, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_placements_and_all_lrm_and_rlm_placements_w_symm = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_placements_and_all_lrm_and_rlm_placements_and_splittings_w_symm = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

point_placement_and_all_321_boundaries_w_symm = {
    "batch_strategies": [all_cell_insertions, all_321_boundaries],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

point_placement_and_all_321_boundaries_and_splittings_w_symm = {
    "batch_strategies": [all_cell_insertions, all_321_boundaries],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_placements_and_all_321_boundaries_w_symm = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_321_boundaries],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_placements_and_all_321_boundaries_and_splittings_w_symm = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_321_boundaries],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

finite_w_symm = {
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

mimic_regular_insertion_encoding_w_symm = {
    "batch_strategies": [all_cell_insertions, minimum_insertion_encoding_row_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [],
    "recursive_strategies": [reversibly_deletable_points],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

mimic_regular_insertion_encoding_flip_w_symm = {
    "batch_strategies": [all_cell_insertions, leftmost_insertion_encoding_column_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [],
    "recursive_strategies": [reversibly_deletable_points],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

mimic_regular_insertion_encoding_but_better_w_symm = {
    "batch_strategies": [all_cell_insertions, minimum_insertion_encoding_row_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

mimic_regular_insertion_encoding_flip_but_better_w_symm = {
    "batch_strategies": [all_cell_insertions, leftmost_insertion_encoding_column_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

mimic_regular_insertion_encoding_but_better_from_all_angles_w_symm = {
    "batch_strategies": [all_cell_insertions, insertion_encoding_row_placements, insertion_encoding_column_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

mimic_Zeilberger_enumeration_schemes_w_symm = {
    "batch_strategies": [all_cell_insertions, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral],
    "recursive_strategies": [reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

left_to_right_maxima_123_and_point_placements_w_symm = {
    "batch_strategies": [all_cell_insertions, left_to_right_maxima123],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

left_to_right_maxima_1234_and_point_placements_w_symm = {
    "batch_strategies": [all_cell_insertions, left_to_right_maxima1234],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

left_to_right_maxima_123_and_row_column_placements_w_symm = {
    "batch_strategies": [all_cell_insertions, left_to_right_maxima123, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

left_to_right_maxima_1234_and_row_column_placements_w_symm = {
    "batch_strategies": [all_cell_insertions, left_to_right_maxima1234, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

point_separation_and_isolation_with_left_to_right_maxima1234_w_symm = {
    "batch_strategies": [all_cell_insertions, left_to_right_maxima1234, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_insertion_w_symm = {
    "batch_strategies": [all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_insertion_and_cell_insertion_w_symm = {
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_insertion_and_cell_insertion_and_point_separation_w_symm = {
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_insertion_and_splittings_w_symm = {
    "batch_strategies": [all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_insertion_and_cell_insertion_and_splittings_w_symm = {
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

row_and_column_insertion_and_cell_insertion_and_point_separation_and_splittings_w_symm = {
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

jays_special_w_symm = {
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_point_placements, all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

jays_special_no_rec_w_symm = {
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_point_placements, all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

extreme_points_w_symm = {
    "batch_strategies": [extreme_point_boundaries, all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_point_placements, all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": True,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

# --------------------------------------------------------------------------
# Below is an exact copy of the strategy packs at the top, but without interleaving recursions
# --------------------------------------------------------------------------

all_strategies_non_interl = {
    "batch_strategies": [all_cell_insertions, all_point_isolations],
    "equivalence_strategies": [all_point_placements, point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

minimum_row_placements_non_interl = {
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

minimum_row_placements_and_splittings_non_interl = {
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

minimum_row_no_rec_non_interl = {
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

minimum_row_placements_and_point_separation_non_interl = {
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

minimum_row_placements_and_splittings_and_point_separation_non_interl = {
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

row_placements_non_interl = {
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

row_placements_and_splittings_non_interl = {
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

row_placements_no_rec_non_interl = {
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

row_placements_and_point_separation_non_interl = {
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

row_placements_and_splittings_and_point_separation_non_interl = {
    "batch_strategies": [all_cell_insertions, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

left_column_placements_non_interl = {
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

left_column_placements_and_splittings_non_interl = {
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

left_column_placements_no_rec_non_interl = {
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

left_column_placements_and_point_separation_non_interl = {
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

left_column_placements_and_splittings_and_point_separation_non_interl = {
    "batch_strategies": [all_cell_insertions, all_leftmost_column_placements],
    "equivalence_strategies": [all_equivalent_leftmost_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

column_placements_non_interl = {
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

column_placements_and_splittings_non_interl = {
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

column_placements_no_rec_non_interl = {
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

column_placements_and_point_separation_non_interl = {
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

column_placements_and_splittings_and_point_separation_non_interl = {
    "batch_strategies": [all_cell_insertions, all_column_placements],
    "equivalence_strategies": [all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

row_and_column_placements_non_interl = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

row_and_column_placements_and_splittings_non_interl = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

row_and_column_placements_no_rec_non_interl = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

row_and_column_placements_and_point_separation_non_interl = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

row_and_column_placements_and_splittings_and_point_separation_non_interl = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

point_placement_non_interl = {
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

point_placement_and_splittings_non_interl = {
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

point_placement_and_point_separation_non_interl = {
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

point_placement_and_splittings_and_point_separation_non_interl = {
    "batch_strategies": [all_cell_insertions],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

point_separation_and_isolation_non_interl = {
    "batch_strategies": [all_cell_insertions, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

point_separation_and_isolation_and_splittings_non_interl = {
    "batch_strategies": [all_cell_insertions, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

point_placement_and_all_lrm_and_rlm_placements_non_interl = {
    "batch_strategies": [all_cell_insertions, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

point_placement_and_all_lrm_and_rlm_placements_and_splittings_non_interl = {
    "batch_strategies": [all_cell_insertions, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

row_and_column_placements_and_all_lrm_and_rlm_placements_non_interl = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

row_and_column_placements_and_all_lrm_and_rlm_placements_and_splittings_non_interl = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_lrm_and_rlm_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

point_placement_and_all_321_boundaries_non_interl = {
    "batch_strategies": [all_cell_insertions, all_321_boundaries],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

point_placement_and_all_321_boundaries_and_splittings_non_interl = {
    "batch_strategies": [all_cell_insertions, all_321_boundaries],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

row_and_column_placements_and_all_321_boundaries_non_interl = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_321_boundaries],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

row_and_column_placements_and_all_321_boundaries_and_splittings_non_interl = {
    "batch_strategies": [all_cell_insertions, all_row_placements, all_column_placements, all_321_boundaries],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

finite_non_interl = {
    "batch_strategies": [all_cell_insertions, all_minimum_row_placements],
    "equivalence_strategies": [all_equivalent_minimum_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

mimic_regular_insertion_encoding_non_interl = {
    "batch_strategies": [all_cell_insertions, minimum_insertion_encoding_row_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [],
    "recursive_strategies": [reversibly_deletable_points],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

mimic_regular_insertion_encoding_flip_non_interl = {
    "batch_strategies": [all_cell_insertions, leftmost_insertion_encoding_column_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [],
    "recursive_strategies": [reversibly_deletable_points],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

mimic_regular_insertion_encoding_but_better_non_interl = {
    "batch_strategies": [all_cell_insertions, minimum_insertion_encoding_row_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

mimic_regular_insertion_encoding_flip_but_better_non_interl = {
    "batch_strategies": [all_cell_insertions, leftmost_insertion_encoding_column_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

mimic_regular_insertion_encoding_but_better_from_all_angles_non_interl = {
    "batch_strategies": [all_cell_insertions, insertion_encoding_row_placements, insertion_encoding_column_placements],
    "equivalence_strategies": [],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

mimic_Zeilberger_enumeration_schemes_non_interl = {
    "batch_strategies": [all_cell_insertions, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral],
    "recursive_strategies": [reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

left_to_right_maxima_123_and_point_placements_non_interl = {
    "batch_strategies": [all_cell_insertions, left_to_right_maxima123],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

left_to_right_maxima_1234_and_point_placements_non_interl = {
    "batch_strategies": [all_cell_insertions, left_to_right_maxima1234],
    "equivalence_strategies": [all_point_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

left_to_right_maxima_123_and_row_column_placements_non_interl = {
    "batch_strategies": [all_cell_insertions, left_to_right_maxima123, all_row_placements],
    "equivalence_strategies": [all_equivalent_row_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

left_to_right_maxima_1234_and_row_column_placements_non_interl = {
    "batch_strategies": [all_cell_insertions, left_to_right_maxima1234, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

point_separation_and_isolation_with_left_to_right_maxima1234_non_interl = {
    "batch_strategies": [all_cell_insertions, left_to_right_maxima1234, all_point_isolations],
    "equivalence_strategies": [point_separation, all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

row_and_column_insertion_non_interl = {
    "batch_strategies": [all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

row_and_column_insertion_and_cell_insertion_non_interl = {
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

row_and_column_insertion_and_cell_insertion_and_point_separation_non_interl = {
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

row_and_column_insertion_and_splittings_non_interl = {
    "batch_strategies": [all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

row_and_column_insertion_and_cell_insertion_and_splittings_non_interl = {
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

row_and_column_insertion_and_cell_insertion_and_point_separation_and_splittings_non_interl = {
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

jays_special_non_interl = {
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_point_placements, all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

jays_special_no_rec_non_interl = {
    "batch_strategies": [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_point_placements, all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

extreme_points_non_interl = {
    "batch_strategies": [extreme_point_boundaries, all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
    "equivalence_strategies": [all_point_placements, all_equivalent_point_isolations, point_separation],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [splittings],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": True,
    "early_splitting_only": False
    }

classical_binary_pattern_placement  = {
    "batch_strategies": [classical_binary_pattern, all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

binary_pattern_classical_class_placement  = {
    "batch_strategies": [binary_pattern_classical_class, all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }

binary_pattern_placement  = {
    "batch_strategies": [classical_binary_pattern, all_cell_insertions, all_row_placements, all_column_placements],
    "equivalence_strategies": [all_equivalent_row_placements, all_equivalent_column_placements],
    "inferral_strategies": [empty_cell_inferral, row_and_column_separation, subclass_inferral],
    "recursive_strategies": [components, reversibly_deletable_cells],
    "verification_strategies": [subset_verified, is_empty],
    "symmetry": False,
    "non_interleaving_recursion": False,
    "early_splitting_only": False
    }
