from grids import Block
from grids import PositiveClass
from grids import Tiling

from atrap.tools import cells_of_occurrences
from itertools import chain

from .batch_class import BatchStrategy


__all__ = ["all_cell_insertions"]


def all_cell_insertions(tiling, **kwargs):
    """Yield all cell insertions of a tiling along with a formal step."""
    # We are concerned with all the classes of the tiling
    for cell, block in tiling.classes:
        # Format the formal step string
        positive_class = PositiveClass(block)
        format_string = "We perform cell insertion into cell {}; either it is empty or {}."  # TODO: References
        formal_step = format_string.format(tuple(cell), positive_class)
        # Yield the formal step and the pair of tilings created

        yield BatchStrategy( formal_step, cell_insertion(tiling, cell) )


def cell_insertion(tiling, cell):
    """Cell insert into a specific cell."""
    # Create a dict copy of the tiling
    new_tiling_dict = dict(tiling)
    # Create the tiling where the class has been removed
    block = new_tiling_dict.pop(cell)
    if block is Block.point or isinstance(block, PositiveClass):
        raise ValueError("Attempting to cell insert on non-class block.")
    empty_cell_tiling = Tiling(new_tiling_dict)
    # Create the positive class of the class in question
    positive_class = PositiveClass(block)
    # Create the tiling where the class has been replaced with the positive class
    new_tiling_dict[cell] = positive_class
    positive_tiling = Tiling(new_tiling_dict)
    return empty_cell_tiling, positive_tiling


def all_active_cell_insertions(tiling, basis, basis_partitioning=None, **kwargs):
    """Yield all cell insertions where the cell was used for a some bad pattern of a tiling along with a formal step."""
    # We are concerned with all the classes of the tiling
    if len(tiling) <= 1:
        for strategy in all_cell_insertions(tiling):
            yield strategy
        return

    cells_to_insert = set( chain( *cells_of_occurrences(tiling, basis, basis_partitioning=basis_partitioning)) )
    for cell in cells_to_insert:
        block = tiling[cell]
        if isinstance(block, PositiveClass) or block is Block.point:
            continue
        positive_class = PositiveClass(block)
        format_string = "We perform cell insertion into cell {}; either it is empty or {}."  # TODO: References
        formal_step = format_string.format(tuple(cell), positive_class)
        # Yield the formal step and the pair of tilings created
        yield BatchStrategy( formal_step, cell_insertion(tiling, cell) )
