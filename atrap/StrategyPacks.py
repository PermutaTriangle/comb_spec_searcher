from atrap.strategies import *


class StrategyPacks(object):
    """Different strategy packs for convenience."""

    # Avoiding all_symmetric_tilings on purpose.
    all_strategies = [
        [all_cell_insertions, all_point_isolations],
        [all_point_placements, point_separation, all_equivalent_point_isolations],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, is_empty]]

    minimum_row_placements = [
        [all_cell_insertions, all_minimum_row_placements],
        [all_equivalent_minimum_row_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    minimum_row_placements_and_splittings = [
        [all_cell_insertions, all_minimum_row_placements],
        [all_equivalent_minimum_row_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, is_empty]]

    minimum_row_no_rec = [
        [all_cell_insertions, all_minimum_row_placements],
        [all_equivalent_minimum_row_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [],
        [subset_verified, is_empty]]

    minimum_row_placements_and_point_separation = [
        [all_cell_insertions, all_minimum_row_placements],
        [all_equivalent_minimum_row_placements, point_separation],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    minimum_row_placements_and_splittings_and_point_separation = [
        [all_cell_insertions, all_minimum_row_placements],
        [all_equivalent_minimum_row_placements, point_separation],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, is_empty]]

    row_placements = [
        [all_cell_insertions, all_row_placements],
        [all_equivalent_row_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    row_placements_and_splittings = [
        [all_cell_insertions, all_row_placements],
        [all_equivalent_row_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, is_empty]]

    row_placements_no_rec = [
        [all_cell_insertions, all_row_placements],
        [all_equivalent_row_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [],
        [subset_verified, is_empty]]

    row_placements_and_point_separation = [
        [all_cell_insertions, all_row_placements],
        [all_equivalent_row_placements, point_separation],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    row_placements_and_splittings_and_point_separation = [
        [all_cell_insertions, all_row_placements],
        [all_equivalent_row_placements, point_separation],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, is_empty]]

    left_column_placements = [
        [all_cell_insertions, all_leftmost_column_placements],
        [all_equivalent_leftmost_column_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    left_column_placements_and_splittings = [
        [all_cell_insertions, all_leftmost_column_placements],
        [all_equivalent_leftmost_column_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, is_empty]]

    left_column_placements_no_rec = [
        [all_cell_insertions, all_leftmost_column_placements],
        [all_equivalent_leftmost_column_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [],
        [subset_verified, is_empty]]

    left_column_placements_and_point_separation = [
        [all_cell_insertions, all_leftmost_column_placements],
        [all_equivalent_leftmost_column_placements, point_separation],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    left_column_placements_and_splittings_and_point_separation = [
        [all_cell_insertions, all_leftmost_column_placements],
        [all_equivalent_leftmost_column_placements, point_separation],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, is_empty]]

    column_placements = [
        [all_cell_insertions, all_column_placements],
        [all_equivalent_column_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    column_placements_and_splittings = [
        [all_cell_insertions, all_column_placements],
        [all_equivalent_column_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, is_empty]]

    column_placements_no_rec = [
        [all_cell_insertions, all_column_placements],
        [all_equivalent_column_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [],
        [subset_verified, is_empty]]

    column_placements_and_point_separation = [
        [all_cell_insertions, all_column_placements],
        [all_equivalent_column_placements, point_separation],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    column_placements_and_splittings_and_point_separation = [
        [all_cell_insertions, all_column_placements],
        [all_equivalent_column_placements, point_separation],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, is_empty]]

    row_and_column_placements = [
        [all_cell_insertions, all_row_placements, all_column_placements],
        [all_equivalent_row_placements, all_equivalent_column_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    row_and_column_placements_and_splittings = [
        [all_cell_insertions, all_row_placements, all_column_placements],
        [all_equivalent_row_placements, all_equivalent_column_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, is_empty]]

    row_and_column_placements_no_rec = [
        [all_cell_insertions, all_row_placements, all_column_placements],
        [all_equivalent_row_placements, all_equivalent_column_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    row_and_column_placements_and_point_separation = [
        [all_cell_insertions, all_row_placements, all_column_placements],
        [all_equivalent_row_placements, all_equivalent_column_placements, point_separation],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    row_and_column_placements_and_splittings_and_point_separation = [
        [all_cell_insertions, all_row_placements, all_column_placements],
        [all_equivalent_row_placements, all_equivalent_column_placements, point_separation],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, is_empty]]

    point_placement = [
        [all_cell_insertions],
        [all_point_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    point_placement_and_splittings = [
        [all_cell_insertions],
        [all_point_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, is_empty]]

    point_placement_and_point_separation = [
        [all_cell_insertions],
        [all_point_placements, point_separation],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    point_placement_and_splittings_and_point_separation = [
        [all_cell_insertions],
        [all_point_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, is_empty]]

    point_separation_and_isolation = [
        [all_cell_insertions, all_point_isolations],
        [point_separation, all_equivalent_point_isolations],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    point_separation_and_isolation_and_splittings = [
        [all_cell_insertions, all_point_isolations],
        [point_separation, all_equivalent_point_isolations],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, is_empty]]

    point_placement_and_all_lrm_and_rlm_placements = [
        [all_cell_insertions, all_lrm_and_rlm_placements],
        [all_point_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    point_placement_and_all_lrm_and_rlm_placements_and_splittings = [
        [all_cell_insertions, all_lrm_and_rlm_placements],
        [all_point_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, is_empty]]

    row_and_column_placements_and_all_lrm_and_rlm_placements = [
        [all_cell_insertions, all_row_placements, all_column_placements, all_lrm_and_rlm_placements],
        [all_equivalent_row_placements, all_equivalent_column_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    row_and_column_placements_and_all_lrm_and_rlm_placements_and_splittings = [
        [all_cell_insertions, all_row_placements, all_column_placements, all_lrm_and_rlm_placements],
        [all_equivalent_row_placements, all_equivalent_column_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, is_empty]]

    point_placement_and_all_321_boundaries = [
        [all_cell_insertions, all_321_boundaries],
        [all_point_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    point_placement_and_all_321_boundaries_and_splittings = [
        [all_cell_insertions, all_321_boundaries],
        [all_point_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, is_empty]]

    row_and_column_placements_and_all_321_boundaries = [
        [all_cell_insertions, all_row_placements, all_column_placements, all_321_boundaries],
        [all_equivalent_row_placements, all_equivalent_column_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    row_and_column_placements_and_all_321_boundaries_and_splittings = [
        [all_cell_insertions, all_row_placements, all_column_placements, all_321_boundaries],
        [all_equivalent_row_placements, all_equivalent_column_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, is_empty]]

    finite = [
        [all_cell_insertions, all_minimum_row_placements],
        [all_equivalent_minimum_row_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [],
        [subset_verified, is_empty]]

    mimic_regular_insertion_encoding = [
        [all_cell_insertions, minimum_insertion_encoding_row_placements],
        [],
        [],
        [reversibly_deletable_points],
        [subset_verified, is_empty]]

    mimic_regular_insertion_encoding_flip = [
        [all_cell_insertions, leftmost_insertion_encoding_column_placements],
        [],
        [],
        [reversibly_deletable_points],
        [subset_verified, is_empty]]

    mimic_regular_insertion_encoding_but_better = [
        [all_cell_insertions, minimum_insertion_encoding_row_placements],
        [],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    mimic_regular_insertion_encoding_flip_but_better = [
        [all_cell_insertions, leftmost_insertion_encoding_column_placements],
        [],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    mimic_regular_insertion_encoding_but_better_from_all_angles = [
        [all_cell_insertions, insertion_encoding_row_placements, insertion_encoding_column_placements],
        [],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    mimic_Zeilberger_enumeration_schemes = [
        [all_cell_insertions, all_point_isolations],
        [point_separation, all_equivalent_point_isolations],
        [empty_cell_inferral],
        [reversibly_deletable_cells],
        [subset_verified, is_empty]]

    left_to_right_maxima_123_and_point_placements = [
        [all_cell_insertions, left_to_right_maxima123],
        [all_point_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    left_to_right_maxima_1234_and_point_placements = [
        [all_cell_insertions, left_to_right_maxima1234],
        [all_point_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    left_to_right_maxima_123_and_row_column_placements = [
        [all_cell_insertions, left_to_right_maxima123, all_row_placements],
        [all_equivalent_row_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    left_to_right_maxima_1234_and_row_column_placements = [
        [all_cell_insertions, left_to_right_maxima1234, all_row_placements, all_column_placements],
        [all_equivalent_row_placements, all_equivalent_column_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    point_separation_and_isolation_with_left_to_right_maxima1234 = [
        [all_cell_insertions, left_to_right_maxima1234, all_point_isolations],
        [point_separation, all_equivalent_point_isolations],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    row_and_column_insertion = [
        [all_row_and_column_insertions, all_point_isolations],
        [all_equivalent_point_isolations],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    row_and_column_insertion_and_cell_insertion = [
        [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
        [all_equivalent_point_isolations],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    row_and_column_insertion_and_cell_insertion_and_point_separation = [
        [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
        [all_equivalent_point_isolations, point_separation],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    row_and_column_insertion_and_splittings = [
        [all_row_and_column_insertions, all_point_isolations],
        [all_equivalent_point_isolations],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, is_empty]]

    row_and_column_insertion_and_cell_insertion_and_splittings = [
        [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
        [all_equivalent_point_isolations],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, is_empty]]

    row_and_column_insertion_and_cell_insertion_and_point_separation_and_splittings = [
        [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
        [all_equivalent_point_isolations, point_separation],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, is_empty]]

    jays_special = [
        [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
        [all_point_placements, all_equivalent_point_isolations, point_separation],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, is_empty]]

    jays_special_no_rec = [
        [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
        [all_point_placements, all_equivalent_point_isolations, point_separation],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [],
        [subset_verified, is_empty]]

    extreme_points = [
        [extreme_point_boundaries, all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
        [all_point_placements, all_equivalent_point_isolations, point_separation],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, is_empty]]

    def __new__(_cls):
        raise RuntimeError("Block class should not be instantiated")
