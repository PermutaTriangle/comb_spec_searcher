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

    finite = [
        [all_cell_insertions, all_minimum_row_placements],
        [all_equivalent_minimum_row_placements],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [],
        [subset_verified, is_empty]]

    mimic_regular_insertion_encoding = [
        [all_cell_insertions, all_minimum_row_placements],
        [all_equivalent_minimum_row_placements],
        [empty_cell_inferral],
        [reversibly_deletable_points],
        [one_by_one_verification, is_empty]]

    row_and_column_placements_point_separation = [
        [all_cell_insertions, all_row_placements, all_column_placements],
        [all_equivalent_row_placements, all_equivalent_column_placements, point_separation],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [components, reversibly_deletable_cells],
        [subset_verified, is_empty]]

    row_insertion_testing = [
        [all_cell_insertions, all_row_and_column_insertions, all_point_isolations],
        [point_separation, all_equivalent_point_isolations, all_equivalent_row_and_column_insertions],
        [empty_cell_inferral, row_and_column_separation, subclass_inferral],
        [splittings],
        [subset_verified, one_by_one_verification, is_empty]]



    def __new__(_cls):
        raise RuntimeError("Block class should not be instantiated")
